import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import auth, comments, feed, likes, posts, users
from app.core.config import settings
from app.core.database import close_db

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("Starting Social Network API...")
    yield
    logger.info("Shutting down Social Network API...")
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")
app.include_router(likes.router, prefix="/api/v1")
app.include_router(feed.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Social Network API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}
