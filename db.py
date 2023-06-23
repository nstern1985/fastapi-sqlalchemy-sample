from typing import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from enums.DBType import DBType
from settings import settings

database_url: str

match settings.DB_DRIVER:
    case DBType.SQLITE:
        database_url = "sqlite+aiosqlite:///db.sqlite"
    case DBType.POSTGRES:
        assert settings.DB_HOST is not None, "missing DB_HOST"
        assert settings.DB_PORT is not None, "missing DB_PORT"
        assert settings.DB_USERNAME is not None, "missing DB_USER_NAME"
        assert settings.DB_PASSWORD is not None, "missing DB_PASSWORD"
        assert settings.DB_NAME is not None, "missing DB_NAME"
        database_url = f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    case _:
        raise NotImplementedError()

engine = create_async_engine(database_url, echo=True, future=True)


# async def connect():
#     await engine.connect()
#
#
# async def disconnect():
#     await engine.dispose()


async def get_session() -> AsyncIterator[AsyncSession]:
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=True)
    async with async_session() as session:
        yield session
