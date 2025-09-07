import os

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)


class Database:
    def __init__(self):
        username = os.environ.get("POSTGRES_USERNAME")
        password = os.environ.get("POSTGRES_PASSWORD")
        host = os.environ.get("POSTGRES_HOST")
        port = os.environ.get("POSTGRES_PORT")
        database = os.environ.get("POSTGRES_DB")
        DATABASE_URL = (
            f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
        )

        self.engine = create_async_engine(DATABASE_URL, future=True, echo=False)
        self.SessionLocal = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False
        )

    async def get_db(self) -> AsyncSession:
        async with self.SessionLocal() as session:
            yield session
