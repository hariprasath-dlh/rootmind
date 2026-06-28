"""
LangGraph State Machine for RootMind Autonomous Pipeline.
Orchestrates all agents in a stateful workflow with conditional routing.
"""
import traceback
import logging
import json
import time
from datetime import datetime
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END

from backend.agents.anomaly_agent import analyze_logs
from backend.agents.rca_agent import analyze_root_cause

logger = logging.getLogger(__name__)


# ============================================================
# 1. DEFINE THE STATE SCHEMA
# ============================================================
class AgentState(TypedDict):
    """The state that flows through the LangGraph pipeline."""
    raw_logs: dict                    # Input: raw log data
    anomaly_report: Optional[dict]    # Output from Anomaly Agent
    rca_report: Optional[dict]        # Output from RCA Agent
    fix_suggestion: Optional[dict]    # Output from Fix Agent
    postmortem_report: Optional[dict] # Output from Post-Mortem Agent
    status: str                       # Current workflow status
    error: Optional[str]              # Error message if something fails


# ============================================================
# 2. DEFINE THE NODES (Each node is an agent)
# ============================================================

def anomaly_detection_node(state: AgentState) -> dict:
    """Node 1: Run the Anomaly Detection Agent."""
    print("\n" + "="*60)
    print("[NODE 1] Anomaly Detection Agent - Starting")
    print("="*60)
    try:
        result = analyze_logs(state["raw_logs"])
        print(f"[NODE 1] DONE - anomaly detected: {result.get('assessment', {}).get('is_anomaly', False)}")
        return {
            "anomaly_report": result,
            "status": "anomaly_detection_complete"
        }
    except Exception as e:
        print(f"[NODE 1] ERROR - Anomaly Agent failed: {e}")
        traceback.print_exc()
        return {
            "anomaly_report": {"error": str(e)},
            "status": "failed",
            "error": f"Anomaly Agent error: {str(e)}"
        }


def rca_node(state: AgentState) -> dict:
    """Node 2: Run the Root Cause Analysis Agent."""
    print("\n" + "="*60)
    print("[NODE 2] Root Cause Analysis Agent - Starting")
    print("="*60)
    try:
        repo_url = state["raw_logs"].get("repo_url")
        result = analyze_root_cause(state["anomaly_report"], repo_url=repo_url)
        print("[NODE 2] DONE - RCA complete")
        return {
            "rca_report": result,
            "status": "rca_complete"
        }
    except Exception as e:
        print(f"[NODE 2] ERROR - RCA Agent failed: {e}")
        traceback.print_exc()
        return {
            "rca_report": {"error": str(e)},
            "status": "failed",
            "error": f"RCA Agent error: {str(e)}"
        }


def fix_suggester_node(state: AgentState) -> dict:
    """Node 3: Fix Suggester Agent - Generates code patches."""
    from backend.agents.fix_agent import generate_fix

    print("\n" + "="*60)
    print("[NODE 3] Fix Suggester Agent - Starting")
    print("="*60)
    try:
        result = generate_fix(state["rca_report"])
        print("[NODE 3] DONE - Fix suggestion generated")
        return {
            "fix_suggestion": result,
            "status": "fix_suggestion_complete"
        }
    except Exception as e:
        print(f"[NODE 3] ERROR - Fix Suggester failed: {e}")
        traceback.print_exc()
        return {
            "fix_suggestion": {"error": str(e)},
            "status": "failed",
            "error": f"Fix Suggester error: {str(e)}"
        }


def postmortem_writer_node(state: AgentState) -> dict:
    """Node 4: Post-Mortem Writer Agent - Generates incident reports."""
    from backend.agents.postmortem_agent import generate_postmortem
    from backend.models.memory_engine import store_incident

    print("\n" + "="*60)
    print("[NODE 4] Post-Mortem Writer Agent - Starting")
    print("="*60)
    try:
        incident_data = {
            "service": state["raw_logs"].get("service", "unknown"),
            "timestamp": state["raw_logs"].get("timestamp", ""),
            "anomaly_report": state["anomaly_report"],
            "rca_report": state["rca_report"],
            "fix_suggestion": state["fix_suggestion"]
        }

        result = generate_postmortem(incident_data)
        store_incident(incident_data, result["incident_id"])
        print(f"[NODE 4] DONE - Post-mortem written, incident_id={result.get('incident_id')}")
        return {
            "postmortem_report": result,
            "status": "postmortem_complete"
        }
    except Exception as e:
        print(f"[NODE 4] ERROR - Post-Mortem Writer failed: {e}")
        traceback.print_exc()
        return {
            "postmortem_report": {"error": str(e)},
            "status": "failed",
            "error": f"Post-Mortem Writer error: {str(e)}"
        }


def send_slack_alert_node(state: AgentState) -> dict:
    """Node 5: Send Slack alert with full incident details."""
    from backend.services.slack_service import send_alert

    print("\n" + "="*60)
    print("[NODE 5] Slack Alert - Starting")
    print("="*60)
    try:
        incident_data = {
            "service": state["raw_logs"].get("service", "unknown"),
            "anomaly_report": state["anomaly_report"],
            "rca_report": state["rca_report"],
            "fix_suggestion": state["fix_suggestion"],
            "postmortem_report": state["postmortem_report"]
        }

        result = send_alert(incident_data)
        print("[NODE 5] DONE - Slack alert sent")
        return {
            "status": "slack_alert_sent"
        }
    except Exception as e:
        print(f"[NODE 5] ERROR - Slack alert failed: {e}")
        traceback.print_exc()
        return {
            "status": "slack_alert_failed",
            "error": f"Slack alert error: {str(e)}"
        }


# ============================================================
# 3. DEFINE CONDITIONAL ROUTING
# ============================================================
def should_continue_to_rca(state: AgentState) -> str:
    """
    Conditional edge: Decide whether to trigger RCA or end the pipeline.
    Only proceed to RCA if an anomaly was actually detected.
    """
    anomaly_report = state.get("anomaly_report", {}) or {}

    if "error" in anomaly_report:
        print("[ROUTER] Anomaly detection had an error. Ending pipeline.")
        return "end"

    assessment = anomaly_report.get("assessment", {}) or {}
    is_anomaly = assessment.get("is_anomaly", False)

    if is_anomaly:
        print("[ROUTER] Anomaly confirmed! Routing to RCA Agent...")
        return "continue_to_rca"
    else:
        print("[ROUTER] System is normal. No further analysis needed.")
        return "end"


# ============================================================
# 4. BUILD THE GRAPH
# ============================================================
def build_pipeline():
    """Constructs and compiles the LangGraph state machine."""
    workflow = StateGraph(AgentState)

    workflow.add_node("anomaly_detector", anomaly_detection_node)
    workflow.add_node("rca_analyzer", rca_node)
    workflow.add_node("fix_suggester", fix_suggester_node)
    workflow.add_node("postmortem_writer", postmortem_writer_node)
    workflow.add_node("slack_alerter", send_slack_alert_node)

    workflow.set_entry_point("anomaly_detector")

    workflow.add_conditional_edges(
        "anomaly_detector",
        should_continue_to_rca,
        {
            "continue_to_rca": "rca_analyzer",
            "end": END
        }
    )

    workflow.add_edge("rca_analyzer", "fix_suggester")
    workflow.add_edge("fix_suggester", "postmortem_writer")
    workflow.add_edge("postmortem_writer", "slack_alerter")
    workflow.add_edge("slack_alerter", END)

    return workflow.compile()


# ============================================================
# 5. EXPOSE THE PIPELINE FUNCTION
# ============================================================
pipeline = build_pipeline()


def _save_incident_to_db(log_data: dict, final_state: dict) -> None:
    """
    Save the completed incident to the SQLite database using the synchronous session.
    Called after pipeline.invoke() completes.
    """
    try:
        from backend.app.database import SessionLocal
        from backend.models.incident_model import IncidentRecord

        anomaly_report = final_state.get("anomaly_report") or {}
        assessment = anomaly_report.get("assessment") or {}
        is_anomaly = assessment.get("is_anomaly", False)

        if not (is_anomaly or final_state.get("postmortem_report")):
            print("[DB] No anomaly detected - skipping database save.")
            return

        rca = final_state.get("rca_report") or {}
        fix = final_state.get("fix_suggestion") or {}
        pm = final_state.get("postmortem_report") or {}

        # Determine incident ID
        inc_id = pm.get("incident_id") or f"INC-{int(time.time())}"

        # Parse timestamp
        ts_str = anomaly_report.get("timestamp")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            except Exception:
                ts = datetime.utcnow()
        else:
            ts = datetime.utcnow()

        # Metrics
        features = assessment.get("features") or {}
        cpu = features.get("cpu_usage") or log_data.get("cpu_usage") or 0.0
        mem = features.get("memory_usage") or log_data.get("memory_usage") or 0.0
        lat = features.get("request_latency_ms") or log_data.get("request_latency_ms") or 0.0
        err = features.get("error_rate") or log_data.get("error_rate") or 0.0
        score = assessment.get("anomaly_score") or 0.0

        # RCA fields
        root_cause_val = rca.get("root_cause") or {}
        if isinstance(root_cause_val, dict):
            root_cause_summary = root_cause_val.get("root_cause_summary") or ""
            tech_exp = root_cause_val.get("technical_explanation") or ""
            resp_file = root_cause_val.get("responsible_file") or ""
            susp_commit = root_cause_val.get("suspected_commit") or ""
        else:
            root_cause_summary = str(root_cause_val)
            tech_exp = ""
            resp_file = ""
            susp_commit = ""

        # Fix fields
        fix_val = fix.get("fix") or {}
        patch = fix_val.get("patch_diff") or fix_val.get("fixed_code") or ""
        explanation = fix_val.get("explanation") or ""
        risk = fix_val.get("risk_level") or "MEDIUM"
        suggestions = fix_val.get("testing_suggestions") or []

        post_mortem_val = pm.get("report") or ""
        pipeline_status = final_state.get("status", "unknown")
        db_status = "resolved" if pipeline_status in ["postmortem_complete", "slack_alert_sent", "slack_alert_failed"] else "open"

        db = SessionLocal()
        try:
            record = IncidentRecord(
                id=inc_id,
                service=anomaly_report.get("service") or log_data.get("service", "unknown"),
                timestamp=ts,
                cpu_usage=float(cpu),
                memory_usage=float(mem),
                latency_ms=float(lat),
                error_rate=float(err),
                anomaly_score=float(score),
                root_cause=root_cause_summary,
                technical_explanation=tech_exp,
                responsible_file=resp_file,
                suspected_commit=susp_commit,
                fix_patch=patch,
                fix_explanation=explanation,
                risk_level=risk,
                testing_suggestions=json.dumps(suggestions),
                post_mortem=post_mortem_val,
                status=db_status,
                pipeline_status=pipeline_status,
            )
            db.merge(record)
            db.commit()
            print(f"[DB] Incident {inc_id} saved to database successfully.")
        except Exception as db_err:
            print(f"[DB] ERROR - Failed to save incident: {db_err}")
            traceback.print_exc()
            db.rollback()
        finally:
            db.close()

    except Exception as outer_err:
        print(f"[DB] OUTER ERROR - {outer_err}")
        traceback.print_exc()


async def run_pipeline(log_data: dict) -> dict:
    """
    Main entry point for the autonomous pipeline.
    Takes raw log data and returns the complete state after all agents run.
    """
    print("\n" + "="*60)
    print("ROOTMIND AUTONOMOUS PIPELINE - STARTING")
    print("="*60)

    try:
        initial_state: AgentState = {
            "raw_logs": log_data,
            "anomaly_report": None,
            "rca_report": None,
            "fix_suggestion": None,
            "postmortem_report": None,
            "status": "starting",
            "error": None
        }

        # pipeline.invoke() is synchronous (LangGraph uses sync by default)
        final_state = pipeline.invoke(initial_state)

        print("\n" + "="*60)
        print(f"PIPELINE COMPLETE - Final Status: {final_state.get('status', 'unknown')}")
        print("="*60 + "\n")

        # Save to database (sync call)
        _save_incident_to_db(log_data, final_state)

        return final_state

    except Exception as e:
        print("\n>>> FULL PIPELINE ERROR <<<")
        traceback.print_exc()
        print(">>> END ERROR <<<\n")
        raise