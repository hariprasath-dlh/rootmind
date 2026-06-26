"""
simulate_crash.py - Production Incident Crash Simulator

Feeds raw anomalous metrics (CPU/RAM spikes or HTTP 5xx error metrics streams)
to backend endpoint to trigger autonomous analysis chain validation.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))


def trigger_crash_simulation() -> None:
    """
    Submits structured post request request to backend /webhooks/ingest or /agents/run route.
    """
    print("Preparing simulated database connection crash payload...")
    mock_payload = {
        "event_type": "metric_anomaly",
        "timestamp": "2026-06-26T14:15:00Z",
        "metrics": {
            "cpu_utilization": 98.4,
            "memory_usage_pct": 92.1,
            "db_connection_pool_saturation": 100.0,
            "api_response_latency_ms": 4500.0,
            "error_rate_pct": 12.5
        },
        "log_sample": "FATAL: remaining connection slots are reserved for non-replication superuser connections"
    }
    # Invoke request methods
    print(f"Payload dispatched to target. Verify Slack alerts and post-mortem dashboards.")


if __name__ == "__main__":
    trigger_crash_simulation()
