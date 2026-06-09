# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Security Scanner — a FastAPI service that detects prompt injection attacks against LLM-powered applications. It runs a detection pipeline (pattern rules → heuristics → classifier → optional LLM fallback) and stores results in PostgreSQL. The MVP is complete.

## Commands

### Running the App
```bash
docker compose up --build        # API on :8000, PostgreSQL on :5432
# API docs: http://localhost:8000/docs
```

### Running Tests
```bash
pytest                                                          # all tests
pytest tests/unit/detection/test_patterns.py -v                # single file
pytest --cov=core --cov=services --cov=db --cov-report=html    # with coverage
```

### Linting & Formatting
```bash
ruff check .          # lint
ruff check . --fix    # lint + autofix
ruff format .         # format
```

### Dashboard (Next.js frontend — not yet integrated)
```bash
cd dashboard && npm run dev    # dev server
cd dashboard && npm run build  # production build
```

## Architecture

The pipeline for a scan request flows through four layers:

```
FastAPI routes → Services → Core Detection Engine → DB Repositories
```

**Detection pipeline** (`core/detection/engine.py`):
1. `RuleRegistry.evaluate(text)` — regex/pattern matching for known injection signatures
2. `HeuristicAnalyzer.analyze(text)` — structural anomalies (delimiter abuse, encoding obfuscation, instruction density)
3. `Classifier.classify(rule_matches, heuristic_results)` — produces `DetectionResult` objects; sets `needs_llm` flag if confidence is low
4. `LLMFallbackClassifier.classify(text)` — calls Anthropic API only when `needs_llm=True` and `ANTHROPIC_API_KEY` is set
5. `RiskScorer.score(detections)` → `risk_score` (0–100) and `risk_level` (LOW/MEDIUM/HIGH/CRITICAL)

**Report generation** (`services/report_service.py`):  
Queries scans in a date window, aggregates into `risk_distribution`, `attack_type_breakdown`, `top_risks`, and `mitigations` (static lookup table per attack type). Stored in the `Report` model's JSONB `data` column.

## Key Conventions

**Async-first:** All DB operations use `async def`, `AsyncSession`, and `await`. Never use synchronous SQLAlchemy in this codebase.

**Pydantic v2:** Use `model_config = ConfigDict(from_attributes=True)` — not the deprecated `class Config`.

**Repository pattern:** Services depend on repositories (e.g., `ScanRepository`), never on the DB session directly.

**Type hints:** Use `X | None` syntax (not `Optional[X]`). Python 3.11+.

**UUID primary keys:** All entity IDs are `UUID(as_uuid=True)` with `default=uuid.uuid4`.

**No Alembic migrations yet:** Schema is initialized at startup via `Base.metadata.create_all` in the FastAPI lifespan. If you add models, import them in `db/models/__init__.py` so they're registered with `Base`.

## Configuration

Copy `.env.example` to `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_security_scanner
ANTHROPIC_API_KEY=           # optional — enables LLM fallback
LLM_FALLBACK_THRESHOLD=0.6   # trigger LLM fallback below this confidence score
```

Settings are loaded via Pydantic `BaseSettings` in `config/settings.py`. The Anthropic model is set in settings (`anthropic_model`), not hardcoded in routes.

## Attack Types

The detection engine classifies detections into five types used throughout the codebase:
`direct_injection`, `indirect_injection`, `jailbreak`, `data_exfiltration`, `obfuscation`

These strings are the canonical values in `Detection.attack_type`, the `attack_type_breakdown` report field, and the mitigations lookup table in `ReportService`.
