"""
Agent trigger and status endpoints.
"""
import traceback # <-- Add this import at the top of the file

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.agents.anomaly_agent import analyze_logs
from backend.agents.rca_agent import analyze_root_cause

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
async def trigger_autonomous_pipeline(payload: LogPayload):
    """
    Receives a log payload. 
    1. Runs Anomaly Detection.
    2. If anomaly detected, automatically triggers Root Cause Analysis (RCA).
    """
    try:
        log_data = payload.model_dump()
        
        # Step 1: Anomaly Detection
        anomaly_result = analyze_logs(log_data)
        
        final_response = {
            "status": "success",
            "anomaly_assessment": anomaly_result,
            "rca_report": None
        }
        
        # Step 2: If anomaly detected, trigger RCA automatically!
        if anomaly_result["assessment"]["is_anomaly"]:
            print("🚨 Anomaly detected! Triggering RCA Agent automatically...")
            rca_result = analyze_root_cause(anomaly_result)
            final_response["rca_report"] = rca_result
            
        return final_response
        
    except Exception as e:
        # 🔥 THIS WILL PRINT THE EXACT ERROR TO YOUR TERMINAL
        print("\n🔥 FULL TRACEBACK:")
        traceback.print_exc()
        print("🔥 END TRACEBACK\n")
        raise HTTPException(status_code=500, detail=str(e))