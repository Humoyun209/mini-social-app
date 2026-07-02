# Mini Social Network API

[![CI](https://github.com/humoyun209/mini-social-app/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/ci.yml)

Backend для мини-социальной сети на FastAPI.

## Возможности

- **Аутентификация**: регистрация, логин, JWT-токены, верификация email
- **Публикации**: CRUD с пагинацией, поиском и фильтрацией по дате
- **Комментарии**: добавление и удаление
- **Лайки**: с ограничениями (нельзя лайкать свой пост, один лайк на пост)
- **Фид**: список пользователей с их публикациями и лайками
- **Фоновые задачи**: Celery для очистки неверифицированных пользователей
- **Мониторинг**: Flower для отслеживания задач Celery

## Стек

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL 16
- Redis 7
- Celery + Flower
- Alembic
- pytest

## Быстрый старт (Docker)

```bash
# Собрать и запустить
docker-compose up -d --build

# Проверить статус
docker-compose ps

# Открыть документацию
open http://localhost:8000/docs

# Открыть Flower
open http://localhost:5555
