# 🌐 Mini Social Network API

[![CI](https://github.com/humoyun209/mini-social-app/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)]()

Backend for a mini social network built with **FastAPI**, featuring async database operations, JWT authentication, background tasks, and CI/CD.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start (Docker)](#-quick-start-docker)
- [Quick Start (Local)](#-quick-start-local)
- [Tests](#-tests)
- [API Endpoints](#-api-endpoints)
- [Environment Variables](#-environment-variables)
- [CI/CD](#-cicd)
- [Pre-commit Hooks](#-pre-commit-hooks)
- [License](#-license)

---

## 🚀 Features

### Authentication & Authorization
- User registration with email and password validation
- JWT authentication (access tokens)
- Email verification via token (link sent to email)
- Resend verification email
- Permission levels: **unverified** / **verified** user

### Posts
- CRUD operations (create, read, update, delete)
- Pagination (`page`, `page_size`)
- Search by `title` and `content` (LIKE)
- Filter by creation date (`date_from`, `date_to`)
- Like and comment counters on each post

### Comments
- Add comments to posts
- Delete own comments
- List comments for a post

### Likes
- Like / unlike a post
- Like status (check if current user liked)
- Restrictions:
  - ❌ Cannot like your own post
  - ❌ One like per user per post
  - ✅ Available even for unverified users

### Feed
- List of users with their posts and likes
- Pagination
- Two endpoints: `/feed` and `/all`

### Background Tasks
- **Celery worker** — task execution
- **Celery beat** — periodic scheduling
- **Flower** — web monitoring for tasks
- Automatic cleanup of unverified users (default: older than 48 hours, daily at 03:00 UTC)

---

## 🛠 Tech Stack

| Category | Technology |
|----------|-----------|
| Framework | FastAPI, Uvicorn |
| Language | Python 3.12 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Cache / Broker | Redis 7 |
| Background Tasks | Celery + Flower |
| Authentication | PyJWT, bcrypt |
| Validation | Pydantic v2 |
| Testing | pytest, pytest-asyncio, pytest-env, httpx |
| Linting | Ruff, Mypy |
| CI/CD | GitHub Actions |
| Pre-commit | pre-commit framework |
| Package Manager | uv |
| Containerization | Docker, Docker Compose |

---

## 📁 Project Structure

```
mini-social-app/
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI
├── app/
│   ├── api/                        # API routers
│   │   ├── auth.py                 # Authentication
│   │   ├── users.py                # Users
│   │   ├── posts.py                # Posts
│   │   ├── comments.py             # Comments
│   │   ├── likes.py                # Likes
│   │   └── feed.py                 # Feed
│   ├── core/                       # Application core
│   │   ├── config.py               # Settings (pydantic-settings)
│   │   ├── database.py             # DB connection (async)
│   │   └── security.py             # JWT, password hashing
│   ├── models/                     # SQLAlchemy models
│   │   ├── base.py                 # Base class (TimestampMixin)
│   │   ├── user.py                 # User
│   │   ├── post.py                 # Post
│   │   ├── comment.py              # Comment
│   │   └── like.py                 # Like
│   ├── schemas/                    # Pydantic schemas (request/response)
│   ├── services/                   # Business logic
│   │   ├── auth_service.py
│   │   ├── post_service.py
│   │   ├── comment_service.py
│   │   ├── like_service.py
│   │   ├── feed_service.py
│   │   └── email_service.py        # Email sending (console mode)
│   ├── tasks/                      # Celery tasks
│   │   ├── celery_app.py           # Celery setup
│   │   └── cleanup_tasks.py        # Unverified users cleanup
│   └── main.py                     # FastAPI entry point
├── alembic/                        # DB migrations
│   └── versions/
├── docker/
│   └── dev/
│       └── Dockerfile
├── tests/                          # Tests
│   ├── conftest.py                 # Fixtures
│   ├── test_auth.py
│   ├── test_posts.py
│   ├── test_comments.py
│   ├── test_likes.py
│   ├── test_feed.py
│   └── test_permissions.py
├── .env                            # Local environment variables
├── .env.test                       # Test variables
├── .env.docker                     # Docker variables
├── .env.example                    # Variables template
├── .pre-commit-config.yaml         # Pre-commit hooks
├── docker-compose.yml              # Docker Compose
├── pyproject.toml                  # Dependencies and configs
└── README.md
```

---

## 🐳 Quick Start (Docker)

### Requirements
- Docker
- Docker Compose

### Run

```bash
# 1. Clone the repository
git clone https://github.com/your-username/mini-social-app.git
cd mini-social-app

# 2. Build and start all services
docker-compose up -d --build

# 3. Check status
docker-compose ps
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| **FastAPI** | `8000` | REST API |
| **PostgreSQL** | `5432` | Database |
| **Redis** | `6380` | Celery broker |
| **Celery Worker** | — | Background task processing |
| **Celery Beat** | — | Periodic tasks |
| **Flower** | `5555` | Celery monitoring |

### Useful Links

- 📄 **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- 📄 **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- 🌸 **Flower:** [http://localhost:5555](http://localhost:5555)
- ❤️ **Health check:** [http://localhost:8000/health](http://localhost:8000/health)

### Stop

```bash
# Stop services
docker-compose down

# Stop and remove data (clean start)
docker-compose down -v
```

---

## 💻 Quick Start (Local)

### Requirements
- Python 3.12+
- PostgreSQL 16
- Redis 7
- [uv](https://docs.astral.sh/uv/) (package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/mini-social-app.git
cd mini-social-app

# 2. Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
uv sync --all-groups

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your settings

# 5. Start PostgreSQL and Redis

# 6. Create database
psql -U postgres -c "CREATE DATABASE social_network;"

# 7. Apply migrations
uv run alembic upgrade head
```

### Run Services

**Terminal 1 — FastAPI:**
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Celery Worker:**
```bash
# Windows
uv run celery -A app.tasks.celery_app worker --loglevel=info --pool=solo

# Linux/Mac
uv run celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 3 — Celery Beat:**
```bash
uv run celery -A app.tasks.celery_app beat --loglevel=info
```

**Terminal 4 — Flower (optional):**
```bash
uv run celery -A app.tasks.celery_app flower --port=5555 --broker=redis://localhost:6379/0
```

---

## 🧪 Tests

### Setup

```bash
# Create test database
psql -U postgres -c "CREATE DATABASE social_network_test;"
```

### Run

```bash
# All tests
uv run pytest tests/ -v

# With code coverage
uv run pytest tests/ -v --cov=app --cov-report=term-missing

# Specific file only
uv run pytest tests/test_auth.py -v

# With verbose output
uv run pytest tests/ -v -s
```

### Test Coverage

| File | Coverage |
|------|----------|
| `test_auth.py` | Registration, login, verification, resend, me |
| `test_posts.py` | CRUD, pagination, search, date filter, 404 |
| `test_comments.py` | Create, list, delete, 404 |
| `test_likes.py` | Like/unlike, own post, duplicate, status |
| `test_feed.py` | /feed, /all, pagination, structure |
| `test_permissions.py` | Access rights, 401/403/404 codes |

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/api/v1/auth/register` | Register new user | Public |
| `POST` | `/api/v1/auth/login` | Login, get JWT | Public |
| `GET` | `/api/v1/auth/verify?token=xxx` | Verify email | Public |
| `POST` | `/api/v1/auth/resend-verification-email` | Resend verification email | Public |
| `GET` | `/api/v1/auth/me` | Current user | 🔒 Token |

### Users

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `PATCH` | `/api/v1/users/me` | Update profile | 🔒 Verified |

### Posts

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/v1/posts` | List (pagination, search, filter) | Public |
| `POST` | `/api/v1/posts` | Create post | 🔒 Verified |
| `GET` | `/api/v1/posts/{id}` | Get by ID | Public |
| `PATCH` | `/api/v1/posts/{id}` | Update (author only) | 🔒 Verified |
| `DELETE` | `/api/v1/posts/{id}` | Delete (author only) | 🔒 Verified |

### Comments

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/v1/posts/{id}/comments` | List comments | Public |
| `POST` | `/api/v1/posts/{id}/comments` | Add comment | 🔒 Verified |
| `DELETE` | `/api/v1/comments/{id}` | Delete (author only) | 🔒 Verified |

### Likes

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/api/v1/posts/{id}/like` | Like a post | 🔒 Token |
| `DELETE` | `/api/v1/posts/{id}/like` | Unlike a post | 🔒 Token |
| `GET` | `/api/v1/posts/{id}/like/status` | Like status | 🔒 Token |

### Feed

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/v1/feed` | Users with posts and likes | Public |
| `GET` | `/api/v1/all` | Alias for /feed | Public |

> 🔒 **Token** — requires JWT token in `Authorization: Bearer <token>` header
> 🔒 **Verified** — requires JWT token + verified email

---

## 🔧 Environment Variables

### `.env` (local development)

```bash
# Application
APP_NAME=Social Network API
APP_VERSION=0.1.0
DEBUG=true

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=social_network

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Verification
VERIFICATION_TOKEN_EXPIRE_HOURS=24
UNVERIFIED_USER_CLEANUP_HOURS=48
```

---

## 🔄 CI/CD

The project uses **GitHub Actions** for automated code checks.

### Pipeline

```
Push / Pull Request
       │
       ▼
┌─────────────┐
│    Lint      │ ← ruff check, ruff format, mypy
└──────┬──────┘
       │ pass
       ▼
┌─────────────┐
│    Test      │ ← pytest with PostgreSQL and Redis
└─────────────┘
```

### What's Checked

1. **Lint** — `ruff check app/ tests/`
2. **Format** — `ruff format --check app/ tests/`
3. **Types** — `mypy app/`
4. **Tests** — `pytest tests/ -v --cov=app`

### Local Check Before Push

```bash
# Linting
uv run ruff check app/ tests/
uv run ruff format --check app/ tests/

# Types
uv run mypy app/

# Tests
uv run pytest tests/ -v
```

---

## 🪝 Pre-commit Hooks

Automatic code checks on every `git commit`.

### Installation

```bash
uv add --group dev pre-commit
uv run pre-commit install
```

### What's Checked

| Hook | Description |
|------|-------------|
| `ruff` | Linting with auto-fix |
| `ruff-format` | Code formatting |
| `mypy` | Type checking |
| `trailing-whitespace` | Remove trailing whitespace |
| `end-of-file-fixer` | Fix end of file |
| `check-yaml` | YAML validation |
| `check-added-large-files` | Protect against large files |
| `check-merge-conflict` | Check for merge conflicts |
| `debug-statements` | Protect against print/breakpoint |

### Usage

```bash
# Hooks run automatically on commit
git commit -m "feat: add feature"

# Manual run on all files
uv run pre-commit run --all-files

# Skip hooks (WIP)
git commit -m "wip" --no-verify
```

---

## 🎁 Implemented Bonus Features

- ✅ **GitHub Actions CI** — automatic linting, type checking, and tests on push/PR
- ✅ **Pre-commit hooks** — ruff, mypy, formatting, protection against junk in commits
- ✅ **Celery beat** — periodic cleanup of unverified users
- ✅ **Flower** — web interface for Celery task monitoring
- ✅ **Docker Compose** — full stack in a single `docker-compose up`

---

## 📝 Request Examples

### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john",
    "full_name": "John Doe",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Create Post

```bash
curl -X POST http://localhost:8000/api/v1/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "title": "My First Post",
    "content": "Hello World!"
  }'
```

### List Posts with Search

```bash
curl "http://localhost:8000/api/v1/posts?search=Python&page=1&page_size=10"
```