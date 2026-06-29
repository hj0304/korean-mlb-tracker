from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    CHAR,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Player(Base):
    __tablename__ = "players"

    # MLB player ID, used as-is (not auto-generated).
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    full_name_en: Mapped[str] = mapped_column(Text, nullable=False)
    full_name_ko: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[str] = mapped_column(Text, nullable=False)
    player_type: Mapped[str] = mapped_column(Text, nullable=False)  # batter | pitcher | two_way
    current_team_id: Mapped[int | None] = mapped_column(BigInteger)
    current_level: Mapped[str | None] = mapped_column(Text)  # MLB | AAA | AA | A+ | A
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    birth_date: Mapped[date | None] = mapped_column(Date)
    bats: Mapped[str | None] = mapped_column(CHAR(1))  # L | R | S
    throws: Mapped[str | None] = mapped_column(CHAR(1))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    abbrev: Mapped[str] = mapped_column(Text, nullable=False)
    league: Mapped[str | None] = mapped_column(Text)  # AL | NL | MiLB
    level: Mapped[str | None] = mapped_column(Text)


class SeasonStats(Base):
    __tablename__ = "season_stats"

    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("players.id"), primary_key=True)
    season: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_name: Mapped[str] = mapped_column(Text, primary_key=True)  # hitting | pitching | fielding
    level: Mapped[str] = mapped_column(Text, primary_key=True)  # MLB | AAA | AA | A+ | A | R
    team_id: Mapped[int | None] = mapped_column(BigInteger)  # null = multi-team season
    stats: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GameLog(Base):
    __tablename__ = "game_logs"

    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("players.id"), primary_key=True)
    game_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    game_date: Mapped[date] = mapped_column(Date, nullable=False)
    opponent_id: Mapped[int | None] = mapped_column(BigInteger)
    is_home: Mapped[bool | None] = mapped_column(Boolean)
    level: Mapped[str | None] = mapped_column(Text)  # MLB | AAA | AA | A+ | A | R
    group_name: Mapped[str] = mapped_column(Text, primary_key=True)  # hitting | pitching
    stats: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_game_logs_date", text("game_date DESC")),
        Index("idx_game_logs_player_date", "player_id", text("game_date DESC")),
    )


class EtlRun(Base):
    __tablename__ = "etl_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # daily_games | season_stats | roster_sync
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(Text, nullable=False)  # running | success | failed
    error: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
