"""
LangGraph State Machine for RootMind Autonomous Pipeline.
Orchestrates all agents in a stateful workflow with conditional routing.
"""
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END

from backend.agents.anomaly_agent import analyze_logs
from backend.agents.rca_agent import analyze_root_cause


# ============================================================
# 1. DEFINE THE STATE SCHEMA
# ============================================================
class AgentState(TypedDict):
    """The state that flows through the LangGraph pipeline."""
    raw_logs: dict                    # Input: raw log data
    anomaly_report: Optional[dict]    # Output from Anomaly Agent
    rca_report: Optional[dict]        # Output from RCA Agent
    fix_suggestion: Optional[dict]    # Output from Fix Agent (stub)
    postmortem_report: Optional[dict] # Output from Post-Mortem Agent (stub)
    status: str                       # Current workflow status
    error: Optional[str]              # Error message if something fails


# ============================================================
# 2. DEFINE THE NODES (Each node is an agent)
# ============================================================
def anomaly_detection_node(state: AgentState) -> dict:
    """Node 1: Run the Anomaly Detection Agent."""
    print("\n" + "="*60)
    print("🔍 [NODE 1] Anomaly Detection Agent - Starting")
    print("="*60)
    try:
        result = analyze_logs(state["raw_logs"])
        return {
            "anomaly_report": result,
            "status": "anomaly_detection_complete"
        }
    except Exception as e:
        print(f"❌ Anomaly Agent failed: {e}")
        return {
            "anomaly_report": {"error": str(e)},
            "status": "failed",
            "error": f"Anomaly Agent error: {str(e)}"
        }


def rca_node(state: AgentState) -> dict:
    """Node 2: Run the Root Cause Analysis Agent."""
    print("\n" + "="*60)
    print("🔎 [NODE 2] Root Cause Analysis Agent - Starting")
    print("="*60)
    try:
        result = analyze_root_cause(state["anomaly_report"])
        return {
            "rca_report": result,
            "status": "rca_complete"
        }
    except Exception as e:
        print(f"❌ RCA Agent failed: {e}")
        return {
            "rca_report": {"error": str(e)},
            "status": "failed",
            "error": f"RCA Agent error: {str(e)}"
        }


def fix_suggester_node(state: AgentState) -> dict:
    """Node 3: Fix Suggester Agent - Generates code patches."""
    from backend.agents.fix_agent import generate_fix
    
    print("\n" + "="*60)
    print("🛠️  [NODE 3] Fix Suggester Agent - Starting")
    print("="*60)
    try:
        result = generate_fix(state["rca_report"])
        return {
            "fix_suggestion": result,
            "status": "fix_suggestion_complete"
        }
    except Exception as e:
        print(f"❌ Fix Suggester failed: {e}")
        return {
            "fix_suggestion": {"error": str(e)},
            "status": "failed",
            "error": f"Fix Suggester error: {str(e)}"
        }


def postmortem_writer_node(state: AgentState) -> dict:
    """Node 4: Post-Mortem Writer Agent (STUB - will be built in Phase 5)."""
    print("\n" + "="*60)
    print("📄 [NODE 4] Post-Mortem Writer Agent - Starting (STUB)")
    print("="*60)
    print("⚠️  Post-Mortem Writer will be implemented in Phase 5")
    return {
        "postmortem_report": {
            "agent": "postmortem_writer",
            "status": "pending_implementation",
            "message": "Post-mortem will be generated in Phase 5"
        },
        "status": "postmortem_complete"
    }


# ============================================================
# 3. DEFINE CONDITIONAL ROUTING
# ============================================================
def should_continue_to_rca(state: AgentState) -> str:
    """
    Conditional edge: Decide whether to trigger RCA or end the pipeline.
    Only proceed to RCA if an anomaly was actually detected.
    """
    anomaly_report = state.get("anomaly_report", {})
    
    # Check if there was an error in anomaly detection
    if "error" in anomaly_report:
        print("⚠️  Anomaly detection had an error. Ending pipeline.")
        return "end"
    
    # Check if anomaly was detected
    assessment = anomaly_report.get("assessment", {})
    is_anomaly = assessment.get("is_anomaly", False)
    
    if is_anomaly:
        print("🚨 Anomaly confirmed! Routing to RCA Agent...")
        return "continue_to_rca"
    else:
        print("✅ System is normal. No further analysis needed.")
        return "end"


# ============================================================
# 4. BUILD THE GRAPH
# ============================================================
def send_slack_alert_node(state: AgentState) -> dict:
    """Node 5: Send Slack alert with full incident details."""
    from backend.services.slack_service import send_alert
    
    print("\n" + "="*60)
    print("💬 [NODE 5] Slack Alert - Starting")
    print("="*60)
    try:
        # Prepare data for Slack
        incident_data = {
            "service": state["raw_logs"].get("service", "unknown"),
            "anomaly_report": state["anomaly_report"],
            "rca_report": state["rca_report"],
            "fix_suggestion": state["fix_suggestion"],
            "postmortem_report": state["postmortem_report"]
        }
        
        result = send_alert(incident_data)
        return {
            "status": "slack_alert_sent"
        }
    except Exception as e:
        print(f"❌ Slack alert failed: {e}")
        return {
            "status": "slack_alert_failed",
            "error": f"Slack alert error: {str(e)}"
        }


def build_pipeline():
    """Constructs and compiles the LangGraph state machine."""
    
    # Initialize the state graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("anomaly_detector", anomaly_detection_node)
    workflow.add_node("rca_analyzer", rca_node)
    workflow.add_node("fix_suggester", fix_suggester_node)
    workflow.add_node("postmortem_writer", postmortem_writer_node)
    workflow.add_node("slack_alerter", send_slack_alert_node)
    
    # Set entry point
    workflow.set_entry_point("anomaly_detector")
    
    # Add conditional edge after anomaly detection
    workflow.add_conditional_edges(
        "anomaly_detector",
        should_continue_to_rca,
        {
            "continue_to_rca": "rca_analyzer",
            "end": END
        }
    )
    
    # Linear flow for the rest
    workflow.add_edge("rca_analyzer", "fix_suggester")
    workflow.add_edge("fix_suggester", "postmortem_writer")
    workflow.add_edge("postmortem_writer", "slack_alerter")
    workflow.add_edge("slack_alerter", END)
    
    # Compile the graph
    return workflow.compile()


# ============================================================
# 5. EXPOSE THE PIPELINE FUNCTION
# ============================================================
pipeline = build_pipeline()

def run_pipeline(log_data: dict) -> dict:
    """
    Main entry point for the autonomous pipeline.
    Takes raw log data and returns the complete state after all agents run.
    """
    print("\n" + "🚀"*30)
    print("🚀 ROOTMIND AUTONOMOUS PIPELINE - STARTING")
    print("🚀"*30)
    
    # Initialize the state
    initial_state: AgentState = {
        "raw_logs": log_data,
        "anomaly_report": None,
        "rca_report": None,
        "fix_suggestion": None,
        "postmortem_report": None,
        "status": "starting",
        "error": None
    }
    
    # Run the pipeline
    final_state = pipeline.invoke(initial_state)
    
    print("\n" + "✅"*30)
    print(f"✅ PIPELINE COMPLETE - Final Status: {final_state['status']}")
    print("✅"*30 + "\n")
    
    return final_state