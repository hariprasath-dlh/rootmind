"""
Agent trigger and status endpoints.
Uses LangGraph to orchestrate the autonomous pipeline.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.agents.graph import run_pipeline

router = APIRouter()
class LogPayload(BaseModel):
    """Schema for incoming log data."""
    service: str
    timestamp: str
    cpu_usage: float
    memory_usage: float
    request_latency_ms: float
    error_rate: float
    raw_log: Optional[str] = None
    repo_url: Optional[str] = None


@router.post("/run")
async def run_autonomous_pipeline(payload: LogPayload):
    """
    Triggers the full LangGraph autonomous pipeline.
    
    Flow:
    1. Anomaly Detection (always runs)
    2. Root Cause Analysis (only if anomaly detected)
    3. Fix Suggestion (stub - Phase 4)
    4. Post-Mortem Writer (stub - Phase 5)
    """
    try:
        log_data = payload.model_dump()
        final_state = await run_pipeline(log_data)
        return {
            "status": "success",
            "pipeline_status": final_state["status"],
            "anomaly_assessment": final_state.get("anomaly_report"),
            "rca_report": final_state.get("rca_report"),
            "fix_suggestion": final_state.get("fix_suggestion"),
            "postmortem_report": final_state.get("postmortem_report"),
            "error": final_state.get("error")
        }
        
    except Exception as e:
        import traceback
        print("\n? FULL TRACEBACK:")
        traceback.print_exc()
        print("? END TRACEBACK\n")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{run_id}")
async def get_pipeline_status(run_id: str):
    """Get the status of a pipeline run (placeholder for future implementation)."""
    return {
        "run_id": run_id,
        "status": "not_implemented",
        "message": "Pipeline status tracking will be added in a future phase"
    }