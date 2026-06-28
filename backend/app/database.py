"""
Database connection and session management for RootMind.
Provides both async (for FastAPI routes) and sync (for pipeline saves) sessions.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Declarative base shared by all models
# ---------------------------------------------------------------------------
Base = declarative_base()

# ---------------------------------------------------------------------------
# Async engine + session (used by FastAPI route handlers)
# ---------------------------------------------------------------------------
async_url = settings.DATABASE_URL  # e.g. sqlite+aiosqlite:///./rootmind.db
engine = create_async_engine(async_url, echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ---------------------------------------------------------------------------
# Synchronous engine + session (used by pipeline save after invoke())
# ---------------------------------------------------------------------------
sync_url = async_url.replace("sqlite+aiosqlite", "sqlite")
sync_engine = create_engine(sync_url, echo=settings.DEBUG)
SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


# ---------------------------------------------------------------------------
# FastAPI dependency ? yields an async session
# ---------------------------------------------------------------------------
async def get_db():
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Startup helper ? creates tables using the SYNC engine so it works in both
# sync and async startup events
# ---------------------------------------------------------------------------
def init_db():
    """Create all database tables (synchronous ? safe to call from startup event)."""
    from backend.models.incident_model import Incident  # Ensure model is registered
    Base.metadata.create_all(bind=sync_engine)
    print("[DB] Database tables created / verified.")