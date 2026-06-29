"""Shared fixtures, including a real-Postgres integration harness (testcontainers).

The integration fixtures skip automatically when Docker isn't available, so the
unit suite still runs locally without Docker. CI (ubuntu) has Docker, so they run
there.
"""

from collections.abc import AsyncGenerator, Generator
from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.deps import get_session
from app.api.v1 import dashboard as dashboard_api
from app.api.v1 import players as players_api
from app.db.base import Base
from app.db.models import GameLog, Player, SeasonStats, Team
from app.main import app


@pytest.fixture(autouse=True)
def _clear_api_caches() -> Generator[None, None, None]:
    # The read APIs hold module-level TTL caches; clear them around every test so
    # cached responses don't leak between tests with different stub/DB data.
    for cache in (
        players_api._players_cache,
        players_api._player_cache,
        players_api._games_cache,
        dashboard_api._cache,
    ):
        cache.clear()
    yield


@pytest.fixture(scope="session")
def pg_url() -> Generator[str, None, None]:
    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError:
        pytest.skip("testcontainers not installed")
    try:
        container = PostgresContainer("postgres:16-alpine")
        container.start()
    except Exception as exc:  # Docker not running / unavailable
        pytest.skip(f"Docker unavailable for integration tests: {exc}")
    try:
        url = container.get_connection_url().replace("+psycopg2", "+asyncpg")
        if "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        yield url
    finally:
        container.stop()


@pytest.fixture
async def seeded_client(pg_url: str) -> AsyncGenerator[AsyncClient, None]:
    # NullPool: each connection is opened/closed per use, so nothing is shared
    # across event loops between fixture setup and request handling.
    # ssl=False: the testcontainer is plaintext localhost, and it stops asyncpg
    # from probing ~/.postgresql/*.crt — which crashes on non-ASCII home paths
    # (see docs/troubleshooting/07-windows-asyncpg-ssl.md).
    engine = create_async_engine(pg_url, poolclass=NullPool, connect_args={"ssl": False})
    # The container is session-scoped, so drop first: each test starts from a
    # clean schema and seed rows don't leak across tests (e.g. into empty_client).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as session:
        # Opponent teams, so game logs can resolve opponent_id -> name/abbrev.
        session.add_all(
            [
                Team(id=141, name="Toronto Blue Jays", abbrev="TOR", league="AL", level="MLB"),
                Team(id=147, name="New York Yankees", abbrev="NYY", league="AL", level="MLB"),
            ]
        )
        session.add(
            Player(
                id=808975,
                full_name_en="Hyeseong Kim",
                full_name_ko="김혜성",
                position="SS",
                player_type="batter",
                current_team_id=119,
                current_level="MLB",
                is_active=True,
                bats="L",
                throws="R",
                birth_date=date(1999, 1, 27),
            )
        )
        await session.flush()  # parent row must exist before FK-bearing children
        session.add(
            SeasonStats(
                player_id=808975,
                season=2026,
                group_name="hitting",
                level="MLB",
                stats={"avg": ".300", "homeRuns": 5},
            )
        )
        session.add(
            GameLog(
                player_id=808975,
                game_id=822832,
                game_date=date(2026, 4, 6),
                opponent_id=141,
                is_home=False,
                group_name="hitting",
                stats={"hits": 2},
            )
        )
        session.add(
            GameLog(
                player_id=808975,
                game_id=823999,
                game_date=date(2026, 5, 10),
                opponent_id=147,
                is_home=True,
                group_name="hitting",
                stats={"hits": 1},
            )
        )
        await session.commit()

    async def _override() -> AsyncGenerator[AsyncSession, None]:
        async with maker() as session:
            yield session

    app.dependency_overrides[get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.fixture
async def empty_client(pg_url: str) -> AsyncGenerator[AsyncClient, None]:
    # Same harness as seeded_client but with no rows, to exercise the empty-DB
    # path of every read endpoint (S2-13).
    # ssl=False: the testcontainer is plaintext localhost, and it stops asyncpg
    # from probing ~/.postgresql/*.crt — which crashes on non-ASCII home paths
    # (see docs/troubleshooting/07-windows-asyncpg-ssl.md).
    engine = create_async_engine(pg_url, poolclass=NullPool, connect_args={"ssl": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def _override() -> AsyncGenerator[AsyncSession, None]:
        async with maker() as session:
            yield session

    app.dependency_overrides[get_session] = _override
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
