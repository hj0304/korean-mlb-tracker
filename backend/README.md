# Korean MLB Tracker — Backend

FastAPI backend. See top-level [`docs/`](../docs) for the full project context.

## Run locally

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Then open <http://localhost:8000/health> to verify.

## Tests

```bash
uv run pytest
```

## Lint / format / typecheck

```bash
uv run ruff check .
uv run ruff format .
uv run mypy app
```
