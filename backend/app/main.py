"""
Main FastAPI application entry point for RootMind.
Handles CORS, router registration, and startup events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous Multi-Agent AIOps Platform",
    version="0.1.0"
)

# Configure CORS for Frontend (Lovable AI / Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for Render/UptimeRobot."""
    return {"status": "healthy", "service": "RootMind Backend"}

# TODO: Include routers here in Phase 1 Step 5
# from app.routers import incidents, agents
# app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
# app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])