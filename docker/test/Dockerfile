FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync --frozen --all-groups

COPY . .

CMD ["uv", "run", "pytest"]
