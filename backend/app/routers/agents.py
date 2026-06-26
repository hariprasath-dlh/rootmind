"""
Agent trigger and status endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.agents.anomaly_agent import analyze_logs

router = APIRouter()

class LogPayload(BaseModel):
    service: str
    timestamp: str
    cpu_usage: float
    memory_usage: float
    request_latency_ms: float
    error_rate: float
    raw_log: Optional[str] = None

@router.post("/analyze")
async def trigger_anomaly_detection(payload: LogPayload):
    """
    Receives a log payload and triggers the Anomaly Detection Agent.
    """
    try:
        # Convert Pydantic model to dict for the agent
        log_data = payload.model_dump()
        
        # Run the agent
        result = analyze_logs(log_data)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))