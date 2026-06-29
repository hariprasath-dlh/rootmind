"""
test_anomaly.py - Unit tests for anomaly detection

Validates scoring and classification logic of the Anomaly Detection Agent and ML Model.
"""

from agents.anomaly_agent import score_log_metrics
from models.anomaly_model import IsolationForestAnomalyModel


def test_score_log_metrics() -> None:
    """
    Test standard return values mapping for the anomaly agent's scoring module.
    """
    mock_payload = {"cpu": 95.0, "latency": 1200}
    result = score_log_metrics(mock_payload)
    assert "is_anomaly" in result
    assert "anomaly_score" in result
    assert isinstance(result["is_anomaly"], bool)


def test_isolation_forest_model_initialization() -> None:
    """
    Test loading/initialization of the underlying Isolation Forest model object.
    """
    model = IsolationForestAnomalyModel()
    assert model.model_path == "anomaly_forest.joblib"
    assert model.model is None
