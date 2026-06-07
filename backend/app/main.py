import os

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import dashboard, players

# Initialize Sentry before the app is created so startup errors are captured.
# DSN is read from the environment, not Settings, so importing the app in CI
# (no DATABASE_URL) keeps working and Sentry stays off unless SENTRY_DSN is set.
if dsn := os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=dsn,
        environment=os.environ.get("SENTRY_ENVIRONMENT", "development"),
    )

app = FastAPI(title="Korean MLB Tracker API")

# CORS: the browser-side frontend (Vercel) calls this API cross-origin, so its
# origin must be allowed. Comma-separated CORS_ALLOW_ORIGINS env; defaults to
# local Next dev. Read from the environment (like SENTRY_DSN) so CI without it
# still works. The API is read-only, so only GET is allowed.
_cors_origins = os.environ.get("CORS_ALLOW_ORIGINS", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins.split(",") if o.strip()],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(dashboard.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
