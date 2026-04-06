FROM python:3.13-slim AS base

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Disable development dependencies
ENV UV_NO_DEV=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

# Create non-root user
RUN useradd -m appuser

WORKDIR /payment_service

# Copy only dependency files first for caching
COPY pyproject.toml uv.lock .

# Install dependencies into global environment
RUN uv sync --frozen --no-dev
# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

CMD ["/bin/sh", "-c", "alembic upgrade head && uv run ./src/payment_service/main.py"]
EXPOSE 8000
