FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy project files (from root context)
COPY pyproject.toml uv.lock ./
COPY backend/app ./app
COPY backend/ingest ./ingest
COPY data ./data

# Install dependencies with uv
RUN uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
