---
title: RootMind AIOps
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# 🤖 RootMind - Autonomous Multi-Agent AIOps Platform

An autonomous incident response system that detects anomalies, traces root causes using RAG + LLMs, generates code patches, and writes post-mortems automatically.

## 🚀 Features

- **5-Agent LangGraph Pipeline** - Autonomous incident handling
- **ML Anomaly Detection** - Isolation Forest algorithm
- **RAG-Powered Root Cause Analysis** - Qdrant + Groq LLM
- **AI Code Patch Generation** - Automatic fix suggestions
- **Automated Post-Mortem Reports** - Professional markdown reports
- **Slack Integration** - Real-time team notifications
- **GitHub Integration** - Real commit analysis
- **Neon PostgreSQL** - Persistent incident storage

## 📡 API Endpoints

- `GET /health` - Health check
- `POST /api/v1/agents/run` - Trigger autonomous pipeline
- `GET /api/v1/incidents` - List all incidents
- `GET /api/v1/incidents/{id}` - Get incident details
- `GET /api/v1/incidents/stats` - Dashboard statistics

## 🛠️ Tech Stack

- **Backend:** FastAPI, LangGraph, SQLAlchemy
- **AI/ML:** Scikit-learn, SentenceTransformers, Groq (Llama 3)
- **Database:** Neon PostgreSQL, Qdrant Cloud
- **Integrations:** Slack Webhooks, GitHub API

## 📊 Example Usage

```bash
curl -X POST https://YOUR-SPACE.hf.space/api/v1/agents/run \
  -H "Content-Type: application/json" \
  -d '{
    "service": "payment-api",
    "timestamp": "2026-06-28T10:00:00Z",
    "cpu_usage": 98.0,
    "memory_usage": 95.0,
    "request_latency_ms": 4500.0,
    "error_rate": 25.0
  }'
```

## 🔗 Links
Live Frontend: [Vercel URL]
GitHub: [GitHub URL]
Documentation: See README.md in repository

## 📝 License
MIT License
