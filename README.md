# RootMind — Autonomous Multi-Agent AIOps Platform

RootMind is an autonomous, multi-agent AI platform designed to revolutionize incident response and observability in modern software systems. Utilizing specialized AI agents powered by LangGraph and Groq (Llama 3), it automatically detects anomalies, performs Root Cause Analysis (RCA), generates code fixes, posts to Slack, and writes post-mortem reports.

## Architecture

```text
               +-----------------------+
               |  Prometheus/Datadog   |
               |  (Metrics / Webhook)  |
               +-----------+-----------+
                           |
                           v
               +-----------+-----------+
               |     FastAPI Backend   |
               +-----------+-----------+
                           |
                           v
               +-----------+-----------+
               |   LangGraph Orchestrator  |
               +-----+-----+-----+-----+
                     |     |     |
      +--------------+     |     +---------------+
      v                    v                     v
+-----+-----+        +-----+-----+         +-----+-----+
|  Anomaly  |        |    RCA    |         | Fix / PM  |
|  Agent    |        |   Agent   |         |  Agents   |
+-----------+        +-----+-----+         +-----+-----+
                           |                     |
                           v                     v
                    +------+------+       +------+------+
                    | Qdrant DB   |       | Slack/GitHub|
                    | (RAG/Memory)|       | API         |
                    +-------------+       +-------------+
```

## Directory Layout

- `backend/`: Core python code, FastAPI configuration, LangGraph orchestration, databases, and ML models.
- `data/`: Sample logs, mock codebases, and evaluation datasets.
- `frontend/`: Dashboard interface (managed by Lovable AI).
- `scripts/`: Local simulation and automation utilities.

## Setup Instructions

Please refer to the detailed instructions in the `backend/` directory for library dependencies and environmental variables configuration.
