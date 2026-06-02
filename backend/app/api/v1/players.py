"""Players API: list and detail."""

from collections.abc import Sequence
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.db.models import GameLog, Player, SeasonStats
from app.schemas.game import GameLogOut
from app.schemas.player import PlayerDetailOut, PlayerOut, SeasonStatsOut

router = APIRouter(prefix="/api/v1", tags=["players"])


@router.get("/players", response_model=list[PlayerOut])
async def list_players(session: AsyncSession = Depends(get_session)) -> Sequence[Player]:
    result = await session.execute(select(Player).order_by(Player.full_name_en))
    return result.scalars().all()


@router.get("/players/{player_id}", response_model=PlayerDetailOut)
async def get_player(
    player_id: int, session: AsyncSession = Depends(get_session)
) -> PlayerDetailOut:
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


@router.get("/players/{player_id}/games", response_model=list[GameLogOut])
async def list_player_games(
    player_id: int,
    since: date | None = None,
    session: AsyncSession = Depends(get_session),
) -> Sequence[GameLog]:
    stmt = select(GameLog).where(GameLog.player_id == player_id)
    if since is not None:
        stmt = stmt.where(GameLog.game_date >= since)
    stmt = stmt.order_by(GameLog.game_date.desc(), GameLog.group_name)
    result = await session.execute(stmt)
    return result.scalars().all()
