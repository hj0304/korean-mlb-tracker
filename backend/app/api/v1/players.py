"""Players API: list and detail.

Read-only endpoints over data that the ETL refreshes once a day, so results are
served from a short-lived in-process cache (see ``app.core.cache``) to avoid a
Supabase round-trip on every request. A matching ``Cache-Control`` lets the
browser/CDN cache too.
"""

from collections.abc import Sequence
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.cache import TTLCache
from app.db.models import GameLog, Player, SeasonStats
from app.schemas.game import GameLogOut
from app.schemas.player import PlayerDetailOut, PlayerOut, SeasonStatsOut

router = APIRouter(prefix="/api/v1", tags=["players"])

_TTL_SECONDS = 300
_CACHE_CONTROL = f"public, max-age={_TTL_SECONDS}"

_players_cache: TTLCache[list[PlayerOut]] = TTLCache(_TTL_SECONDS)
_player_cache: TTLCache[PlayerDetailOut] = TTLCache(_TTL_SECONDS)
_games_cache: TTLCache[list[GameLogOut]] = TTLCache(_TTL_SECONDS)


async def _build_players(session: AsyncSession) -> list[PlayerOut]:
    result = await session.execute(select(Player).order_by(Player.full_name_en))
    return [PlayerOut.model_validate(p) for p in result.scalars().all()]


async def _build_player(session: AsyncSession, player_id: int) -> PlayerDetailOut:
    player = await session.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    result = await session.execute(
        select(SeasonStats)
        .where(SeasonStats.player_id == player_id)
        .order_by(SeasonStats.season.desc(), SeasonStats.group_name)
    )
    return PlayerDetailOut(
        **PlayerOut.model_validate(player).model_dump(),
        bats=player.bats,
        throws=player.throws,
        birth_date=player.birth_date,
        season_stats=[SeasonStatsOut.model_validate(s) for s in result.scalars().all()],
    )


async def _build_games(
    session: AsyncSession, player_id: int, since: date | None
) -> list[GameLogOut]:
    stmt = select(GameLog).where(GameLog.player_id == player_id)
    if since is not None:
        stmt = stmt.where(GameLog.game_date >= since)
    stmt = stmt.order_by(GameLog.game_date.desc(), GameLog.group_name)
    result = await session.execute(stmt)
    return [GameLogOut.model_validate(g) for g in result.scalars().all()]


@router.get("/players", response_model=list[PlayerOut])
async def list_players(
    response: Response, session: AsyncSession = Depends(get_session)
) -> Sequence[PlayerOut]:
    response.headers["Cache-Control"] = _CACHE_CONTROL
    return await _players_cache.get_or_set("all", lambda: _build_players(session))


@router.get("/players/{player_id}", response_model=PlayerDetailOut)
async def get_player(
    player_id: int, response: Response, session: AsyncSession = Depends(get_session)
) -> PlayerDetailOut:
    response.headers["Cache-Control"] = _CACHE_CONTROL
    return await _player_cache.get_or_set(str(player_id), lambda: _build_player(session, player_id))


@router.get("/players/{player_id}/games", response_model=list[GameLogOut])
async def list_player_games(
    player_id: int,
    response: Response,
    since: date | None = None,
    session: AsyncSession = Depends(get_session),
) -> Sequence[GameLogOut]:
    response.headers["Cache-Control"] = _CACHE_CONTROL
    key = f"{player_id}:{since.isoformat() if since else ''}"
    return await _games_cache.get_or_set(key, lambda: _build_games(session, player_id, since))
