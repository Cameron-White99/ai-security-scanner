# Claude Code Handoff — AI Security Scanner

## Project Location

`C:\Cam Dev\Portfolio\ai-security-scanner`

---

## Current State

The project is fully deployed and working. All features are complete.

### What's Live

| Component | URL |
|---|---|
| Dashboard | https://ai-security-scanner-weld.vercel.app |
| API | https://ai-security-scanner-api-1055821256877.us-central1.run.app |
| API Docs | https://ai-security-scanner-api-1055821256877.us-central1.run.app/docs |

### Infrastructure

| Service | Provider | Notes |
|---|---|---|
| Dashboard | Vercel (Hobby) | Next.js, auto-deploys on push via Vercel Git integration |
| Backend API | GCP Cloud Run | Project: `ai-security-scanner-499001`, region: `us-central1` |
| Database | Neon (serverless PostgreSQL) | Connected via Vercel Marketplace |
| Container Registry | GCP Artifact Registry | `us-central1-docker.pkg.dev/ai-security-scanner-499001/ai-security-scanner/api` |

### CI/CD

- **CI** (`.github/workflows/python-app.yml`) — runs `ruff check`, `ruff format --check`, and `pytest tests/unit/` on push/PR to main
- **Deploy** (`.github/workflows/deploy.yml`) — builds Docker image, pushes to Artifact Registry, deploys to Cloud Run on merge to main
- GitHub secret required: `GCP_SA_KEY` (service account: `github-actions@ai-security-scanner-499001.iam.gserviceaccount.com`)

---

## Completed Features

- [x] Detection engine (pattern matching, heuristics, LLM fallback via Anthropic API)
- [x] Risk scoring model (0–100, levels: LOW / MEDIUM / HIGH / CRITICAL)
- [x] FastAPI REST API — `/api/v1/scans/` and `/api/v1/reports/` endpoints
- [x] PostgreSQL schema with full audit logging
- [x] Security report generation (risk distribution, attack breakdown, mitigations, summary)
- [x] Next.js dashboard (scan form, scan history, scan detail, reports page)
- [x] Docker Compose local development environment
- [x] GCP Cloud Run deployment
- [x] CI/CD pipeline (GitHub Actions)
- [x] Test suite — 76 tests (unit + API), run with `pytest`

---

## Environment Variables

### Cloud Run (backend)

| Variable | Notes |
|---|---|
| `DATABASE_URL` | Must use `postgresql+asyncpg://` prefix. Set in Cloud Run service. |
| `ALLOWED_ORIGINS` | Comma-separated list, e.g. `https://ai-security-scanner-weld.vercel.app` |
| `ANTHROPIC_API_KEY` | Optional — enables LLM fallback for low-confidence detections |

### Vercel (dashboard)

| Variable | Notes |
|---|---|
| `NEXT_PUBLIC_API_URL` | Set to `https://ai-security-scanner-api-1055821256877.us-central1.run.app/api/v1` |
| `DATABASE_URL` | Set automatically by Neon Marketplace integration |

---

## Local Development

```bash
# Backend
cp .env.example .env   # set DATABASE_URL and optionally ANTHROPIC_API_KEY
docker compose up --build

# Dashboard
cd dashboard && npm install && npm run dev

# Tests
cd ai-security-scanner
python -m venv venv && venv/Scripts/activate
pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy asyncpg anthropic pytest pytest-asyncio httpx ruff
pytest tests/ -v
```

---

## Key Conventions

- **Async-first:** All DB operations use `async def`, `AsyncSession`, and `await`
- **Pydantic v2:** Use `model_config = ConfigDict(from_attributes=True)`
- **Repository pattern:** Services depend on repositories, never on the DB session directly
- **Type hints:** Use `X | None` syntax (Python 3.11+)
- **UUID primary keys:** All entity IDs are `UUID(as_uuid=True)` with `default=uuid.uuid4`
- **No Alembic:** Schema initialised at startup via `Base.metadata.create_all`; import new models in `db/models/__init__.py`

---

## Known Issues / Notes

- `ALLOWED_ORIGINS` must be a plain comma-separated string (not JSON array) — pydantic-settings parses it as `str` and `main.py` splits on comma
- The Neon database cold-starts after 5 minutes of inactivity — first request after idle may take ~1s longer
- `venv/` is not committed — recreate locally as described above
