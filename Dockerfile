FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY pyproject.toml .

# Extract and install dependencies without requiring source tree
RUN pip install --no-cache-dir \
    "fastapi>=0.111.0" \
    "uvicorn[standard]>=0.29.0" \
    "pydantic>=2.7.0" \
    "pydantic-settings>=2.2.0" \
    "sqlalchemy>=2.0.0" \
    "asyncpg>=0.29.0" \
    "anthropic>=0.28.0" \
    "pytest>=8.0.0" \
    "pytest-asyncio>=0.23.0" \
    "httpx>=0.27.0" \
    "ruff>=0.4.0"

# Copy source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
