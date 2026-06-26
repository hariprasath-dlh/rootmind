import requests
import json

url = "http://127.0.0.1:8000/api/v1/agents/analyze"
payload = {
    "service": "payment-api",
    "timestamp": "2026-06-26T15:30:00Z",
    "cpu_usage": 95.0,
    "memory_usage": 90.0,
    "request_latency_ms": 5000.0,
    "error_rate": 15.0,
    "raw_log": "async def process_payment(amount): Missing timeout on external API call causes latency spikes"
}

print("🚀 Dispatching anomalous payload to FastAPI backend...")
try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("❌ Failed to contact FastAPI server:", e)
