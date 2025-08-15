from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from app.config import settings


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = settings.database_url or "sqlite+aiosqlite:///./dev.db"
        _engine = create_async_engine(db_url, echo=False, future=True)
    return _engine


def get_session_maker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)
    return _SessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async_session = get_session_maker()
    async with async_session() as session:
        yield session


async def init_db():
    from app.db import models  # noqa: F401
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)