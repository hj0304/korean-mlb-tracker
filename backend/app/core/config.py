import ssl
from functools import lru_cache

import certifi
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Korean players we track, MLB player ID -> Korean name. MLB data has no Korean
# names, so they are mapped here by hand. MiLB prospects are added in S2-01.
KOREAN_PLAYERS: dict[int, str] = {
    808975: "김혜성",
    808982: "이정후",
    673490: "김하성",
    823550: "송성문",
}


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
