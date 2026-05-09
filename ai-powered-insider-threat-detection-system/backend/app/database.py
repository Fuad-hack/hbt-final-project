"""
ITDT Async Database Configuration
SQLAlchemy 2.0 with asyncpg driver for PostgreSQL
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from typing import AsyncGenerator

from app.config import settings

# Create async engine for PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
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


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session"""
    async with AsyncSessionLocal() as session:
        try:
            # Set search path for PostgreSQL schema
            await session.execute(text(f"SET search_path TO {settings.DATABASE_SCHEMA}"))
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database - create schema and tables"""
    # Import all models to register them with Base.metadata
    from app.models import User, LoginSession, FileAccessLog, USBUsageLog, EmailLog
    from app.models import BehavioralFeature, GraphFeature, NLPEmailFeature, MergedFeature
    from app.models import ModelRun, AnomalyScore
    from app.models import XAIExplanation, RedTeamFlag
    
    async with engine.begin() as conn:
        # Create schema
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DATABASE_SCHEMA}"))
        # Create all tables from ORM models
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
