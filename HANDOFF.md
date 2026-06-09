# Claude Code Handoff — AI Security Scanner

## Project Location

`C:\Cam Dev\Portfolio\ai-security-scanner`

---

## Current State

The MVP is running. The following are complete and working:

- Detection engine (pattern matching, heuristics, LLM fallback via Anthropic API)
- Risk scoring model (0–100, levels: LOW / MEDIUM / HIGH / CRITICAL)
- FastAPI REST API with `/api/v1/scans/` endpoints (POST, GET list, GET by id)
- PostgreSQL schema with full audit logging
- Docker Compose local environment
- GitHub repo with full documentation

**Remaining features:**
- [ ] Security report generation ← **build this next**
- [ ] React dashboard
- [ ] GCP Cloud Run deployment
- [ ] CI/CD pipeline

---

## Immediate Task: Report Generation

Build the report generation feature following the exact same patterns already established in the codebase.

### What a Report Contains

Generated from scan data over a specified time window:

- `generated_at` — timestamp
- `from_date` / `to_date` — report time window
- `total_scans` — integer
- `risk_distribution` — count per risk level: `{ LOW, MEDIUM, HIGH, CRITICAL }`
- `attack_type_breakdown` — count per attack type detected
- `top_risks` — top 5 highest risk scans: `{ id, risk_score, risk_level, created_at }` only — no raw input text
- `mitigations` — recommended mitigation per attack type detected (static lookup, see below)
- `summary` — one paragraph plain English summary of the report period

### Mitigation Lookup (static)

```python
MITIGATIONS = {
    "direct_injection": "Validate and sanitise all user inputs before passing to LLM. Implement strict system prompt boundaries and use a separate privileged context for system instructions.",
    "indirect_injection": "Treat all external content (web pages, documents, tool outputs) as untrusted. Apply content filtering before including in LLM context.",
    "jailbreak": "Implement output filtering and behavioural guardrails. Monitor for unusual response patterns and apply rate limiting on high-risk inputs.",
    "data_exfiltration": "Restrict LLM access to sensitive data. Audit all outputs for sensitive content patterns and implement output validation before returning responses.",
    "obfuscation": "Apply decoding and normalisation to inputs before analysis. Detect and flag encoded or obfuscated content for additional scrutiny.",
}
```

---

## Files to Create

Follow existing patterns exactly — same import style, same Pydantic v2 config, same async SQLAlchemy patterns.

### 1. `db/models/report.py`

SQLAlchemy model. Store the report as a JSON column (PostgreSQL JSONB).

Fields:
- `id` — UUID primary key
- `from_date` — DateTime with timezone
- `to_date` — DateTime with timezone
- `total_scans` — Integer
- `data` — JSONB (stores risk_distribution, attack_type_breakdown, top_risks, mitigations, summary)
- `created_at` — DateTime with timezone, server default

### 2. `db/repositories/report_repo.py`

Same pattern as `scan_repo.py`:
- `create(report: Report) -> Report`
- `get_by_id(report_id: UUID) -> Report | None`
- `list(limit, offset) -> list[Report]`

### 3. `services/report_service.py`

Query scans within the time window, aggregate the data, build and persist the report.

Key logic:
- Accept `from_date` and `to_date` as parameters
- Query all scans in window using `ScanRepository` (or direct DB query)
- Compute aggregations
- Look up mitigations for each attack type found
- Generate plain English summary
- Save via `ReportRepository`

### 4. `api/routes/reports.py`

Same pattern as `scans.py`:

```
POST /api/v1/reports/       — Generate report for a time range
GET  /api/v1/reports/       — List all reports
GET  /api/v1/reports/{id}   — Retrieve a specific report
```

Request schema:
```python
class ReportRequest(BaseModel):
    from_date: datetime
    to_date: datetime
```

Response schema should return all report fields cleanly.

### 5. Wire Up

- Add `Report` to `db/models/__init__.py`
- Add `app.include_router(reports.router, prefix=settings.api_prefix)` to `api/main.py`
- Import `Report` model in `main.py` alongside `Scan` and `Detection` so it registers with `Base.metadata`

---

## Existing Conventions to Follow

- **Async SQLAlchemy** throughout — use `AsyncSession`, `await db.execute(...)`, `select(...)` 
- **Pydantic v2** — use `model_config = ConfigDict(from_attributes=True)` not `class Config`
- **Dependency injection** — repos and services are instantiated inside route handlers via `Depends(get_db)`
- **UUIDs** — `UUID(as_uuid=True)` with `default=uuid.uuid4`
- **Timestamps** — `DateTime(timezone=True)` with `server_default=func.now()`
- **Line length** — 100 chars (ruff config in pyproject.toml)
- **Python 3.11+** — use `X | None` union syntax, not `Optional[X]`

---

## Existing File Structure

```
ai-security-scanner/
├── api/
│   ├── main.py
│   ├── middleware/
│   └── routes/
│       ├── scans.py        ← reference this for route patterns
│       └── __init__.py
├── config/
├── core/
│   ├── classification/
│   ├── detection/
│   └── scoring/
├── db/
│   ├── database.py
│   ├── models/
│   │   ├── scan.py         ← reference this for model patterns
│   │   ├── detection.py
│   │   └── __init__.py
│   └── repositories/
│       └── scan_repo.py    ← reference this for repo patterns
├── reports/                ← currently empty, ignore this directory
├── services/
│   └── scan_service.py     ← reference this for service patterns
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

---

## Key Settings

- API prefix: `/api/v1` (from `config/settings.py`)
- Database: PostgreSQL via asyncpg
- Container: Docker Compose — `docker compose up --build`
- Docs: `http://localhost:8000/docs`

---

## After Report Generation Is Complete

Next features in order:

1. React / Next.js dashboard — visualise scan history and reports
2. GCP Cloud Run deployment
3. CI/CD pipeline (GitHub Actions)
