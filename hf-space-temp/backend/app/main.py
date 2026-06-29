"""
Main FastAPI application entry point for RootMind.
Handles CORS, router registration, and startup events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import get_settings
from backend.app.routers import agents, incidents # <-- IMPORT ROUTERS

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous Multi-Agent AIOps Platform",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    from backend.app.database import init_db
    init_db()  # Sync call ? creates tables using the sync engine

# Configure CORS for Frontend (Lovable AI / Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://vercel.app",
        "https://huggingface.co",
        "https://*.hf.space",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for Render/UptimeRobot."""
    return {"status": "healthy", "service": "RootMind Backend"}

# Register the routers
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])