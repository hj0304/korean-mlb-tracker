"""Dashboard API: the latest game day's feed across all tracked players."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.cache import TTLCache
from app.db.models import GameLog, Player
from app.schemas.dashboard import DashboardGameOut, DashboardOut

router = APIRouter(prefix="/api/v1", tags=["dashboard"])

_TTL_SECONDS = 300
_CACHE_CONTROL = f"public, max-age={_TTL_SECONDS}"
_cache: TTLCache[DashboardOut] = TTLCache(_TTL_SECONDS)


async def _build_today(session: AsyncSession) -> DashboardOut:
    latest = (await session.execute(select(func.max(GameLog.game_date)))).scalar()
    if latest is None:
        return DashboardOut(date=None, games=[])
    rows = (
        await session.execute(
            select(GameLog, Player)
            .join(Player, Player.id == GameLog.player_id)
            .where(GameLog.game_date == latest)
            .order_by(Player.full_name_en, GameLog.group_name)
        )
    ).all()
    games = [
        DashboardGameOut(
            player_id=p.id,
            full_name_ko=p.full_name_ko,
            full_name_en=p.full_name_en,
            current_level=p.current_level,
            player_type=p.player_type,
            opponent_id=g.opponent_id,
            is_home=g.is_home,
            group_name=g.group_name,
            stats=g.stats,
        )
        for g, p in rows
    ]
    return DashboardOut(date=latest, games=games)


@router.get("/dashboard/today", response_model=DashboardOut)
async def dashboard_today(
    response: Response, session: AsyncSession = Depends(get_session)
) -> DashboardOut:
    response.headers["Cache-Control"] = _CACHE_CONTROL
    return await _cache.get_or_set("today", lambda: _build_today(session))
