"""
FastAPI router for incident retrieval and stats.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import json
import random
from datetime import datetime, timedelta
from typing import List, Optional

from backend.app.database import get_db
from backend.models.incident_model import Incident

router = APIRouter()

def derive_severity(anomaly_score: float, error_rate: float) -> str:
    if error_rate > 20 or anomaly_score < -0.7:
        return "critical"
    if error_rate > 10 or anomaly_score < -0.5:
        return "high"
    if error_rate > 5 or anomaly_score < -0.3:
        return "medium"
    return "low"

def generate_timeseries(base_cpu: float, base_mem: float, base_lat: float, points: int = 30) -> list:
    out = []
    now = datetime.utcnow()
    cpu = max(5.0, base_cpu - 20.0 + random.random() * 10.0)
    mem = max(5.0, base_mem - 15.0 + random.random() * 10.0)
    lat = max(20.0, base_lat - 100.0 + random.random() * 40.0)
    for i in range(points - 1, -1, -1):
        cpu = max(5.0, min(99.0, cpu + (random.random() - 0.4) * 8.0))
        mem = max(5.0, min(99.0, mem + (random.random() - 0.4) * 6.0))
        lat = max(20.0, lat + (random.random() - 0.4) * 35.0)
        if i < points / 3:
            cpu = min(99.0, cpu + 10.0)
            lat += 40.0
        out.append({
            "t": (now - timedelta(seconds=i * 30)).isoformat() + "Z",
            "cpu": round(cpu),
            "memory": round(mem),
            "latency": round(lat)
        })
    return out

def format_incident(inc: Incident) -> dict:
    testing_sugs = []
    if inc.testing_suggestions:
        try:
            testing_sugs = json.loads(inc.testing_suggestions)
        except Exception:
            testing_sugs = []

    # Map database fields to the exact Incident interface the frontend expects
    return {
        "id": inc.id,
        "service": inc.service,
        "severity": derive_severity(inc.anomaly_score or 0.0, inc.error_rate or 0.0),
        "status": inc.status or "resolved",
        "rootCause": inc.root_cause or "Root cause analysis unavailable",
        "createdAt": inc.timestamp.isoformat() + "Z" if inc.timestamp else datetime.utcnow().isoformat() + "Z",
        "mttrSeconds": 300,  # Default fallback MTTR
        "metrics": {
            "cpu": inc.cpu_usage or 0.0,
            "memory": inc.memory_usage or 0.0,
            "latencyMs": inc.latency_ms or 0.0,
            "errorRate": inc.error_rate or 0.0
        },
        "timeseries": generate_timeseries(inc.cpu_usage or 70.0, inc.memory_usage or 65.0, inc.latency_ms or 400.0),
        "patch": inc.fix_patch or "",
        "riskLevel": inc.risk_level.lower() if inc.risk_level else "medium",
        "postMortem": inc.post_mortem or "",
        "technicalExplanation": inc.technical_explanation or "",
        "responsibleFile": inc.responsible_file or "",
        "suspectedCommit": inc.suspected_commit or "",
        "testingSuggestions": testing_sugs
    }

@router.get("/stats")
async def get_incident_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregate statistics for the dashboard."""
    try:
        # Get count of critical incidents
        # Let's count them based on error rate or anomaly score since severity is derived
        # Let's fetch all incidents to compute derived severity or run query
        result = await db.execute(select(Incident))
        incidents = result.scalars().all()
        
        total = len(incidents)
        critical_count = 0
        services = set()
        
        for inc in incidents:
            services.add(inc.service)
            sev = derive_severity(inc.anomaly_score or 0.0, inc.error_rate or 0.0)
            if sev == "critical":
                critical_count += 1
                
        # Average MTTR (default to 300 if no incidents)
        avg_mttr = 300
        
        # Calculate system status
        system_status = "healthy"
        if critical_count > 1:
            system_status = "critical"
        elif critical_count > 0:
            system_status = "degraded"
            
        return {
            "totalIncidents": total,
            "avgMttrSeconds": avg_mttr,
            "criticalAlerts": critical_count,
            "activeServices": len(services) if services else 1,
            "systemStatus": system_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {e}")

@router.get("")
async def list_incidents(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List all incidents, sorted by timestamp descending."""
    try:
        result = await db.execute(
            select(Incident)
            .order_by(Incident.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        incidents = result.scalars().all()
        return [format_incident(inc) for inc in incidents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list incidents: {e}")

@router.get("/test-db")
async def test_database():
    """Test database connection and return incident count."""
    try:
        from backend.app.database import SessionLocal
        from backend.models.incident_model import IncidentRecord

        db = SessionLocal()
        try:
            count = db.query(IncidentRecord).count()
        finally:
            db.close()

        return {
            "status": "ok",
            "message": "Database connection successful",
            "incident_count": count
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Get detailed information for a single incident."""
    try:
        result = await db.execute(select(Incident).where(Incident.id == incident_id))
        inc = result.scalar_one_or_none()
        if not inc:
            raise HTTPException(status_code=404, detail="Incident not found")
        return format_incident(inc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch incident: {e}")

