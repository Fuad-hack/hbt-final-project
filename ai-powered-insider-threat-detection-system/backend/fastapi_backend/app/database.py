"""
ITDT Async Database Configuration
SQLAlchemy 2.0 with asyncpg driver
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text
from typing import AsyncGenerator

from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL in debug mode
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,  # Verify connections before use
    future=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()


async def set_search_path(dbapi_conn, connection_record):
    """Set PostgreSQL search path on connection"""
    await dbapi_conn.execute(f"SET search_path TO {settings.DATABASE_SCHEMA}")


# Register the event listener
@event.listens_for(engine.sync_engine, "connect")
def on_connect(dbapi_conn, connection_record):
    """Sync wrapper for async search path setting"""
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(set_search_path(dbapi_conn, connection_record))
    finally:
        loop.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    Handles commit/rollback automatically.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Set search path for this session
            await session.execute(text(f"SET search_path TO {settings.DATABASE_SCHEMA}"))
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database - create tables if they don't exist"""
    async with engine.begin() as conn:
        # Create schema if not exists
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DATABASE_SCHEMA}"))
        await conn.execute(text(f"SET search_path TO {settings.DATABASE_SCHEMA}"))
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()


async def check_db_connection() -> bool:
    """Health check for database connection"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
