import os

import sentry_sdk
from fastapi import FastAPI

# Initialize Sentry before the app is created so startup errors are captured.
# DSN is read from the environment, not Settings, so importing the app in CI
# (no DATABASE_URL) keeps working and Sentry stays off unless SENTRY_DSN is set.
if dsn := os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=dsn,
        environment=os.environ.get("SENTRY_ENVIRONMENT", "development"),
    )

app = FastAPI(title="Korean MLB Tracker API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# TEMPORARY (S0-11 verification): raises so we can confirm Sentry receives the
# event from the deployed backend. Remove once Sentry is verified.
@app.get("/sentry-debug")
def sentry_debug() -> None:
    raise RuntimeError("Sentry backend verification error")
