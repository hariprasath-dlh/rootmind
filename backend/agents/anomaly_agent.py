"""
Anomaly Detection Agent.
Processes incoming log data and uses the Isolation Forest to detect anomalies.
"""
from backend.models.anomaly_model import predict_anomaly

def analyze_logs(log_data: dict) -> dict:
    """
    Main entry point for the Anomaly Agent.
    Extracts features from the log payload and returns the anomaly assessment.
    """
    print(f"🔍 Anomaly Agent analyzing logs for service: {log_data.get('service', 'unknown')}")
    
    # Extract the 4 key metrics from the incoming log data
    features = [
        float(log_data.get("cpu_usage", 0.0)),
        float(log_data.get("memory_usage", 0.0)),
        float(log_data.get("request_latency_ms", 0.0)),
        float(log_data.get("error_rate", 0.0))
    ]
    
    # Call the ML model
    result = predict_anomaly(features)
    
    # Format the agent's output
    agent_output = {
        "agent": "anomaly_detector",
        "status": "completed",
        "service": log_data.get("service", "unknown"),
        "timestamp": log_data.get("timestamp", "unknown"),
        "assessment": result
    }
    
    if result["is_anomaly"]:
        print(f"🚨 ANOMALY DETECTED! Score: {result['anomaly_score']:.4f}")
    else:
        print(f"✅ System normal. Score: {result['anomaly_score']:.4f}")
        
    return agent_output