"""
test_rca.py - Unit tests for RCA agent

Validates context aggregation and Groq reasoning results inside the RCA agent module.
"""

from agents.rca_agent import run_root_cause_analysis


def test_run_root_cause_analysis() -> None:
    """
    Test diagnostics outputs format from the Root Cause Analysis module.
    """
    mock_anomaly = {"is_anomaly": True, "anomaly_score": 0.85}
    mock_context = "Recent commits: a1b2c3d4 - updated db configuration"
    result = run_root_cause_analysis(mock_anomaly, mock_context)
    
    assert result["confidence"] > 0.0
    assert "suspected_file" in result
    assert "suspected_commit" in result
