FROM python:3.12-slim

# Системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir ".[test,dev]" || pip install --no-cache-dir .

RUN pip install --no-cache-dir \
    pytest>=8.3.0 \
    pytest-asyncio>=0.24.0 \
    pytest-env>=1.1.0 \
    pytest-cov>=6.0.0 \
    httpx>=0.27.0 \
    ruff>=0.8.0 \
    mypy>=1.13.0

COPY . .

CMD ["pytest", "tests/", "-v", "--cov=app", "--cov-report=term-missing"]