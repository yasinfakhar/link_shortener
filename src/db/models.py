import os
import uuid
from datetime import datetime

from sqlalchemy.orm import declared_attr
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import create_async_engine

# Base for declarative models
Base = declarative_base()


class ParentBase(Base):
    __abstract__ = True  # Make this class abstract (not mapped to any table)

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    def deleted_at(cls):
        return Column(DateTime, nullable=True)

class UserModel(ParentBase):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    password = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)

class LinkModel(ParentBase):
    __tablename__ = "links"

    # Integer autoincremented primary key starting from 1 by default in PostgreSQL
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    # Original long URL
    original_url = Column(String, nullable=False)

    # Short code (unique, indexed)
    short_code = Column(String, unique=True, index=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("short_code", name="uq_links_short_code"),
    )


async def init_db():
    username = os.environ.get("POSTGRES_USERNAME")
    password = os.environ.get("POSTGRES_PASSWORD")
    host = os.environ.get("POSTGRES_HOST")
    port = os.environ.get("POSTGRES_PORT")
    database = os.environ.get("POSTGRES_DB")
    DATABASE_URL = (
        f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
    )

    engine = create_async_engine(DATABASE_URL, future=True, echo=False)
    async with engine.begin() as conn:
        # Run the synchronous DDL creation in the async context
        await conn.run_sync(Base.metadata.create_all)
