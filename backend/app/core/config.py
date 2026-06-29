import ssl
from functools import lru_cache

import certifi
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Korean players we track, MLB player ID -> Korean name. MLB data has no Korean
# names, so they are mapped here by hand.
KOREAN_PLAYERS: dict[int, str] = {
    # MLB
    808975: "김혜성",
    808982: "이정후",
    673490: "김하성",
    823550: "송성문",
    # MiLB prospects (S2-01)
    678225: "배지환",
    800231: "조원빈",
    805870: "엄형찬",
    807149: "심준석",
    815794: "장현석",
    808970: "고우석",
    806739: "제이든 김",
    829748: "이현승",
    834605: "김성준",
    836688: "문서준",
}

# "명예 한국인" — not Korean-born, but Korean-parent players who suited up for the
# 대한민국 national team in international play (WBC etc.). Tracked as a distinct
# group (players.is_honorary) so the UI can label/filter them separately. (S2-17)
HONORARY_PLAYERS: dict[int, str] = {
    669242: "토미 에드먼",  # Tommy Edman
    641540: "데인 더닝",  # Dane Dunning
    694376: "셰이 위트컴",  # Shay Whitcomb
    663330: "저마이 존스",  # Jahmai Jones
    676617: "라일리 오브라이언",  # Riley O'Brien
}

# MLB Stats API sportId -> our level label. 16 = Rookie (complex leagues), where
# several tracked prospects currently play. Used to label both the roster and
# each season-stats row.
SPORT_ID_TO_LEVEL: dict[int, str] = {1: "MLB", 11: "AAA", 12: "AA", 13: "A+", 14: "A", 16: "R"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str

    @field_validator("database_url")
    @classmethod
    def _ensure_asyncpg_driver(cls, v: str) -> str:
        # Supabase exposes URLs as `postgresql://...`. We use SQLAlchemy + asyncpg,
        # which requires the `postgresql+asyncpg://` dialect prefix.
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


@lru_cache
def get_ssl_context() -> ssl.SSLContext:
    # SSL is required by Supabase pooler, but we explicitly skip cert chain
    # verification (equivalent to libpq's `sslmode=require`):
    #   1. asyncpg's libpq-style default tries to load `~/.postgresql/postgresql.crt`,
    #      which fails on Windows when the user profile contains non-ASCII characters.
    #   2. The Supabase pooler cert chain is not in certifi's bundle, so strict
    #      verification fails with "self-signed certificate in certificate chain".
    # The Supabase URL stays a secret, so the MITM surface here is limited.
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx
