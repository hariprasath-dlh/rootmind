"""
Database connection and session management for RootMind.
Provides both async (for FastAPI routes) and sync (for pipeline saves) sessions.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from backend.app.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Declarative base shared by all models
# ---------------------------------------------------------------------------
Base = declarative_base()

# ---------------------------------------------------------------------------
# Driver mapping and URL parsing for SQLite / PostgreSQL
# ---------------------------------------------------------------------------
db_url = settings.DATABASE_URL or "sqlite+aiosqlite:///./rootmind.db"

if db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
    # Convert postgres:// to postgresql:// as SQLAlchemy requires postgresql://
    base_url = db_url
    if base_url.startswith("postgres://"):
        base_url = base_url.replace("postgres://", "postgresql://", 1)
    
    # Parse URL to adjust query parameters for different drivers
    parsed = urlparse(base_url)
    query_params = parse_qs(parsed.query)
    
    # 1. Async URL: Replace postgresql:// with postgresql+asyncpg://
    # asyncpg doesn't support 'sslmode=require', it expects 'ssl=require'
    async_params = query_params.copy()
    if 'sslmode' in async_params:
        sslmode_val = async_params.pop('sslmode')[0]
        if sslmode_val != 'disable':
            async_params['ssl'] = ['require']
            
    async_query = urlencode(async_params, doseq=True)
    async_url = urlunparse((
        "postgresql+asyncpg",
        parsed.netloc,
        parsed.path,
        parsed.params,
        async_query,
        parsed.fragment
    ))
    
    # 2. Sync URL: Replace postgresql:// with postgresql+psycopg2://
    # psycopg2 fully supports standard 'sslmode' query parameters
    sync_query = urlencode(query_params, doseq=True)
    sync_url = urlunparse((
        "postgresql+psycopg2",
        parsed.netloc,
        parsed.path,
        parsed.params,
        sync_query,
        parsed.fragment
    ))
else:
    # Default to SQLite
    async_url = db_url
    if "sqlite+aiosqlite" in async_url:
        sync_url = async_url.replace("sqlite+aiosqlite", "sqlite")
    else:
        sync_url = async_url


# ---------------------------------------------------------------------------
# Async engine + session (used by FastAPI route handlers)
# ---------------------------------------------------------------------------
engine = create_async_engine(async_url, echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ---------------------------------------------------------------------------
# Synchronous engine + session (used by pipeline save after invoke())
# ---------------------------------------------------------------------------
sync_engine = create_engine(sync_url, echo=settings.DEBUG)
SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


# ---------------------------------------------------------------------------
# FastAPI dependency – yields an async session
# ---------------------------------------------------------------------------
async def get_db():
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Startup helper – creates tables using the SYNC engine so it works in both
# sync and async startup events
# ---------------------------------------------------------------------------
def init_db():
    """Create all database tables (synchronous – safe to call from startup event)."""
    from backend.models.incident_model import Incident  # Ensure model is registered
    try:
        # Test connection using the synchronous engine
        with sync_engine.connect() as conn:
            db_type = "PostgreSQL (Neon)" if "postgresql" in sync_url else "SQLite"
            print(f"[DB] Successfully connected to {db_type} database.")
        
        # Create all tables defined in Base
        Base.metadata.create_all(bind=sync_engine)
        print("[DB] Database tables created / verified successfully.")
    except Exception as conn_err:
        print(f"[DB] CRITICAL ERROR - Failed to connect or initialize database: {conn_err}")
        raise conn_err