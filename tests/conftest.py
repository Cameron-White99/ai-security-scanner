import os
import pytest
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from api.main import app
    from db.database import get_db

    async def override_get_db():
        yield AsyncMock()

    @asynccontextmanager
    async def mock_lifespan(app):
        yield

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = mock_lifespan
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.router.lifespan_context = original_lifespan
    app.dependency_overrides.clear()
