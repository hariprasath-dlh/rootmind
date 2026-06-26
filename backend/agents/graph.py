"""
graph.py - Main LangGraph state machine, node definitions, and workflows

Defines the multi-agent execution pipeline structure, managing the state
flow between Anomaly, RCA, Fix, and Post-Mortem agents.
"""

from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    """
    Main LangGraph state tracking schema for RootMind multi-agent workflow.
    """
    raw_logs: Dict[str, Any]
    anomaly_report: Optional[Dict[str, Any]]
    rca_report: Optional[Dict[str, Any]]
    fix_suggestion: Optional[Dict[str, Any]]
    postmortem_report: Optional[Dict[str, Any]]
    status: str


def anomaly_detection_node(state: AgentState) -> AgentState:
    """
    State machine node to determine if a log pattern contains anomalous behavior.
    Calls anomaly_agent module.
    
    Args:
        state (AgentState): Current graph execution state.

    Returns:
        AgentState: Updated graph state.
    """
    return state


def rca_node(state: AgentState) -> AgentState:
    """
    State machine node to analyze root cause from log and repository artifacts.
    Calls rca_agent module.

    Args:
        state (AgentState): Current graph execution state.

    Returns:
        AgentState: Updated graph state.
    """
    return state


def fix_suggestion_node(state: AgentState) -> AgentState:
    """
    State machine node to draft target code patch and implementation diff.
    Calls fix_agent module.

    Args:
        state (AgentState): Current graph execution state.

    Returns:
        AgentState: Updated graph state.
    """
    return state


def postmortem_node(state: AgentState) -> AgentState:
    """
    State machine node to generate incident post-mortem documentation report.
    Calls postmortem_agent.

    Args:
        state (AgentState): Current graph execution state.

    Returns:
        AgentState: Updated graph state.
    """
    return state


def should_continue(state: AgentState) -> str:
    """
    Conditional routing function logic. Checks if anomaly score is above the threshold.
    
    Args:
        state (AgentState): Current state containing anomaly report.

    Returns:
        str: Next node to route to ("rca_node" or END).
    """
    anomaly = state.get("anomaly_report")
    if anomaly and anomaly.get("is_anomaly", False):
        return "rca_node"
    return END


# Define state machine graph
workflow = StateGraph(AgentState)

# Add node processes
workflow.add_node("anomaly_detection", anomaly_detection_node)
workflow.add_node("rca", rca_node)
workflow.add_node("fix_suggestion", fix_suggestion_node)
workflow.add_node("postmortem", postmortem_node)

# Set starting point entry
workflow.set_entry_point("anomaly_detection")

# Configure conditional and static edges
workflow.add_conditional_edges(
    "anomaly_detection",
    should_continue,
    {
        "rca_node": "rca",
        END: END
    }
)
workflow.add_edge("rca", "fix_suggestion")
workflow.add_edge("fix_suggestion", "postmortem")
workflow.add_edge("postmortem", END)

# Compile graph
app_graph = workflow.compile()
