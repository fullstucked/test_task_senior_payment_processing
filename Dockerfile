FROM python:3.13-slim AS base

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Disable development dependencies
ENV UV_NO_DEV=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

# Create non-root user
RUN useradd -m appuser

WORKDIR .

# Copy only dependency files first for caching
COPY pyproject.toml uv.lock .

# Install dependencies into global environment
RUN uv sync --frozen --no-dev
# Copy application code
COPY . .

# COPY scripts/run_migrations.py /usr/local/bin/run_migrations.py
# RUN chmod +x /usr/local/bin/run_migrations.py
# Switch to non-root user
USER appuser

#CMD ["/bin/sh", "-c" "echo 1111111111111111111111111111111112222222222222222222222222222222\n\n\n\n\n\n\n\n\n\n\n\n\n"]
#CMD ["/bin/sh", "-c","uv", "run alembic revision --autogenerate \"test\" "]
CMD ["/bin/sh", "-c", "alembic upgrade head && uv run ./src/payment_service/main.py"]
EXPOSE 8000
