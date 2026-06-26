# RootMind — Autonomous Multi-Agent AIOps Platform
## SKILL.md — Master Blueprint & AI Execution Instructions

---

## 1. Project Overview

**Project Name:** RootMind — Autonomous Multi-Agent AIOps Platform

**Description:**
RootMind is an autonomous, multi-agent AI platform designed to revolutionize incident response and observability in modern software systems. While traditional monitoring tools like Datadog and PagerDuty only detect that something is broken, RootMind goes several steps further — it uses a chain of specialized AI agents to automatically diagnose the root cause of an incident, trace the exact code commit responsible, suggest actionable code patches, and auto-generate post-mortem reports.

The platform is built on a zero-cost infrastructure strategy, leveraging generous free-tier APIs and cloud services, making it a production-ready, fully deployed, and highly impressive portfolio project. The business goal is to drastically reduce Mean Time To Resolution (MTTR) for software incidents, saving engineering teams hours of manual debugging and thousands of dollars in downtime costs.

---

## 2. Technical Stack

### Backend & AI Orchestration
- **Python 3.11+** — Core programming language
- **FastAPI** — REST API framework for all backend endpoints
- **LangGraph** — Multi-agent state machine orchestration
- **LangChain** — Agent tooling and chain construction

### AI Models & Vector Database
- **Groq API (Llama 3 / Mixtral)** — Fast, free LLM inference for RCA, Fix Suggester, and Post-Mortem agents
- **Scikit-learn (Isolation Forest)** — Unsupervised ML model for anomaly detection
- **Embedding Models (via Groq / HuggingFace free tier)** — Converts codebase into vectors for semantic search
- **Qdrant Cloud (Free Tier)** — Vector database for RAG pipeline and long-term memory

### Infrastructure, Database & Integrations
- **Render (Free Tier)** — Backend hosting
- **Vercel (Free Tier)** — Frontend hosting
- **SQLite / Supabase (Free Tier)** — Relational database for incident records
- **GitHub API** — Fetches commits and codebase context
- **Slack API** — Real-time alert delivery and slash command receiver
- **Docker & Docker Compose** — Containerization for local dev and deployment
- **UptimeRobot (Free Tier)** — Prevents Render free-tier spin-down

### Frontend
- **React + TypeScript** — UI framework
- **TailwindCSS** — Styling
- **Recharts** — Incident dashboards and data visualization
> ⚠️ NOTE: The entire frontend will be generated and managed by **Lovable AI**. AI models must NOT generate any frontend code.

---

## 3. Detailed File Structure

```text
rootmind/
│
├── frontend/                  # [Frontend will be created entirely by Lovable AI. Do not generate any files here.]
│
├── backend/                   # Core Python FastAPI Backend
│   ├── app/
│   │   ├── main.py            # App initialization, CORS middleware, router registration
│   │   ├── config.py          # Environment variable loading and settings management
│   │   ├── database.py        # SQLite / Supabase connection and session management
│   │   └── routers/
│   │       ├── incidents.py   # Incident CRUD endpoints
│   │       ├── agents.py      # Agent trigger and status endpoints
│   │       └── auth.py        # Authentication endpoints (API key based)
│   │
│   ├── agents/                # LangGraph Multi-Agent System
│   │   ├── graph.py           # Main LangGraph state machine, node definitions, workflow
│   │   ├── anomaly_agent.py   # Isolation Forest anomaly detection logic and scoring
│   │   ├── rca_agent.py       # Root Cause Analysis using RAG + Groq LLM
│   │   ├── fix_agent.py       # Code patch and fix suggestion generator
│   │   └── postmortem_agent.py# Automated incident post-mortem report generator
│   │
│   ├── models/                # ML Models & Vector Store Logic
│   │   ├── anomaly_model.py   # Isolation Forest training, inference, and model persistence
│   │   ├── rag_pipeline.py    # Qdrant vector store interactions, chunking, and embedding
│   │   └── memory_engine.py   # Long-term incident memory and pattern recognition engine
│   │
│   ├── services/              # External Service Integrations
│   │   ├── github_service.py  # GitHub API: fetch commits, diffs, and codebase files
│   │   ├── slack_service.py   # Slack API: send alerts, receive slash commands via webhook
│   │   └── groq_service.py    # Groq API wrapper for all LLM inference calls
│   │
│   ├── utils/                 # Shared Utilities
│   │   ├── logger.py          # Centralized logging configuration
│   │   ├── parsers.py         # Log parsers and data formatters
│   │   └── helpers.py         # Reusable helper functions
│   │
│   ├── tests/                 # Pytest Test Suite
│   │   ├── test_anomaly.py    # Unit tests for anomaly detection
│   │   ├── test_rca.py        # Unit tests for RCA agent
│   │   ├── test_fix.py        # Unit tests for fix suggestion agent
│   │   └── test_api.py        # Integration tests for FastAPI endpoints
│   │
│   ├── requirements.txt       # All Python dependencies with pinned versions
│   └── Dockerfile             # Container definition for Render deployment
│
├── data/                      # Sample Data & Test Datasets
│   ├── sample_logs/           # Mock log files for anomaly detection testing
│   ├── mock_codebase/         # Sample repository files for RAG embedding
│   └── test_datasets/         # Labeled datasets for model evaluation
│
├── scripts/                   # Automation Scripts
│   ├── setup.sh               # One-command environment setup script
│   ├── seed_db.py             # Seed SQLite/Supabase with initial data
│   ├── embed_codebase.py      # Script to chunk and embed a repo into Qdrant
│   └── simulate_crash.py      # Script to simulate a production incident for live demo
│
├── docker-compose.yml         # Local development orchestration (backend + Qdrant)
├── .env.example               # Template for all required environment variables
└── README.md                  # Full project documentation and setup guide
```

---

## 4. Detailed Phase Plan (Execution Order)

> ⚠️ STRICT RULE: Do NOT jump phases. Each phase must be fully completed, tested, and verified before moving to the next.

---

### ✅ Phase 1: Foundation & Anomaly Detection

**Goal:** Establish the working backend and the first AI agent.

**Steps:**
1. Scaffold the full `backend/` directory following the file structure exactly.
2. Implement `app/main.py` with FastAPI initialization, CORS middleware, and router registration.
3. Implement `app/config.py` to load all environment variables using `python-dotenv`.
4. Implement `app/database.py` to set up SQLite using SQLAlchemy (with Supabase as an optional upgrade path).
5. Create the `incidents` router with basic CRUD endpoints for incident records.
6. Implement `models/anomaly_model.py` — train Scikit-learn's Isolation Forest on synthetic log metric data and save the model using `joblib`.
7. Implement `agents/anomaly_agent.py` — load the trained model and expose a scoring function that classifies incoming log data as normal or anomalous.
8. Create `data/sample_logs/` with realistic mock log metric files (CPU, memory, latency, error rate) for testing.
9. Write a mock log stream generator (in `scripts/`) that continuously feeds data to the anomaly agent.
10. Write Pytest tests in `tests/test_anomaly.py`.
11. Deploy the basic backend to **Render (Free Tier)**.
12. Set up **UptimeRobot** to ping the health endpoint every 5 minutes to prevent Render spin-down.

**Deliverable:** A live FastAPI backend on Render that can receive log data and return anomaly scores.

---

### ✅ Phase 2: RAG Pipeline & Root Cause Analysis Agent

**Goal:** Give the platform the ability to understand codebases and identify the root cause of anomalies.

**Steps:**
1. Create a **Qdrant Cloud** free-tier cluster and obtain the API key and endpoint URL.
2. Implement `models/rag_pipeline.py`:
   - Connect to Qdrant Cloud.
   - Chunk text files (code, logs, docs) into segments.
   - Embed chunks using a free embedding model (HuggingFace `sentence-transformers` or Groq).
   - Upsert vectors into a Qdrant collection.
   - Implement a `semantic_search(query)` function to retrieve the most relevant chunks.
3. Implement `services/github_service.py`:
   - Use the GitHub REST API (free, unauthenticated for public repos) to fetch commit history, file diffs, and raw file contents from a target repository.
4. Run `scripts/embed_codebase.py` to fetch a sample repository and embed its entire codebase into Qdrant.
5. Implement `services/groq_service.py` as a clean wrapper around the Groq API client.
6. Implement `agents/rca_agent.py`:
   - Receives an anomaly report (type, timestamp, affected metrics) as input.
   - Calls `semantic_search()` to retrieve the most relevant code files and recent commits from Qdrant.
   - Sends the retrieved context + anomaly details to Groq (Llama 3) with a structured prompt.
   - Returns a structured RCA report: identified root cause, responsible file(s), suspected commit hash, and confidence score.
7. Write Pytest tests in `tests/test_rca.py`.

**Deliverable:** The platform can now take an anomaly and identify the most likely code commit and file responsible for it.

---

### ✅ Phase 3: Agent Orchestration with LangGraph

**Goal:** Wire all agents together into an autonomous, self-running workflow.

**Steps:**
1. Define the **LangGraph state schema** in `agents/graph.py` — a typed dictionary holding: `raw_logs`, `anomaly_report`, `rca_report`, `fix_suggestion`, `postmortem_report`, and `status`.
2. Define the following **LangGraph nodes**, each calling the corresponding agent:
   - `anomaly_detection_node` → calls `anomaly_agent.py`
   - `rca_node` → calls `rca_agent.py`
   - `fix_suggestion_node` → calls `fix_agent.py` (stub for now)
   - `postmortem_node` → calls `postmortem_agent.py` (stub for now)
3. Define **conditional edges**: if the anomaly score is above the threshold, route to `rca_node`; otherwise, route to `end`.
4. Compile the graph using `langgraph.graph.StateGraph` and expose a `run_pipeline(log_data)` function.
5. Add the `agents` router in FastAPI (`app/routers/agents.py`) with a `POST /agents/run` endpoint that accepts log data, triggers the LangGraph pipeline, and returns the full state result.
6. Implement robust error handling and fallback logic within the graph (if any node fails, log the error and return partial results gracefully).
7. End-to-end test: send mock log data to `POST /agents/run` and verify the full anomaly → RCA flow completes.

**Deliverable:** A single API call triggers the full autonomous pipeline from log ingestion to root cause identification.

---

### ✅ Phase 4: Fix Suggester, Slack Integration & Webhook Receiver

**Goal:** Complete the actionable response loop — suggest fixes and deliver alerts.

**Steps:**
1. Implement `agents/fix_agent.py`:
   - Receives the RCA report (root cause, file, commit) as input.
   - Fetches the specific file content via `github_service.py`.
   - Sends the file content + root cause to Groq (Llama 3) with a prompt instructing it to generate a specific, line-by-line code patch.
   - Returns a structured fix suggestion: patch diff, explanation, and estimated risk level.
2. Wire `fix_suggestion_node` properly in `agents/graph.py`.
3. Implement `services/slack_service.py`:
   - Use the Slack Incoming Webhooks API (free) to post formatted messages to a Slack channel.
   - Message format should include: incident title, anomaly summary, root cause, fix suggestion, and severity level.
   - Implement a Slack slash command receiver endpoint in FastAPI (`POST /webhooks/slack`) so users can query incident status from Slack.
4. Add a generic **webhook receiver** in FastAPI (`POST /webhooks/ingest`) that accepts payloads from external tools like Prometheus Alertmanager or a Datadog mock, normalizes the data, and feeds it into the LangGraph pipeline.
5. Write Pytest tests in `tests/test_fix.py`.

**Deliverable:** When an incident is detected, the platform autonomously diagnoses it, suggests a code fix, and delivers a full Slack alert — all without human intervention.

---

### ✅ Phase 5: Post-Mortem Writer, Memory Engine & Frontend Handoff

**Goal:** Close the incident loop with documentation and enable learning from past incidents.

**Steps:**
1. Implement `agents/postmortem_agent.py`:
   - Receives the complete incident state (anomaly, RCA, fix) as input.
   - Uses Groq (Llama 3) to generate a professional post-mortem report in Markdown format.
   - Report structure: Incident Summary, Timeline, Root Cause, Impact Assessment, Fix Applied, Preventive Measures.
   - Save the report to the SQLite/Supabase database and return the Markdown string.
2. Wire `postmortem_node` properly in `agents/graph.py`.
3. Implement `models/memory_engine.py`:
   - After each resolved incident, embed the full incident record (anomaly type + RCA + fix) and upsert it into a dedicated Qdrant collection called `incident_memory`.
   - Implement a `find_similar_incidents(current_anomaly)` function that retrieves the top-3 most similar past incidents using semantic search.
   - Integrate this into the RCA agent to provide historical context to the LLM, improving accuracy over time.
4. Expose a `GET /incidents/{id}/postmortem` endpoint in FastAPI to retrieve a post-mortem report by incident ID.
5. **Frontend Handoff to Lovable AI:**
   - Write a clear, structured **API documentation block** (see Section 8 below) listing all backend endpoints, their request/response schemas, and authentication method.
   - Provide this documentation to Lovable AI along with the instruction to generate a React + TypeScript + TailwindCSS dashboard.

**Deliverable:** The platform writes its own incident post-mortems, learns from history, and the backend is ready for frontend connection.

---

### ✅ Phase 6: Final Polish & Zero-Cost Deployment

**Goal:** Containerize, deploy, and validate the complete system end-to-end.

**Steps:**
1. Finalize `backend/Dockerfile` — multi-stage build, non-root user, production-ready.
2. Finalize `docker-compose.yml` for local development (backend + Qdrant local instance).
3. Write the complete `README.md` with: project description, architecture diagram (ASCII), setup instructions, environment variable guide, and demo instructions.
4. Audit all services against free-tier limits:
   - Groq API: requests per minute limits → implement request caching and batching.
   - Qdrant Cloud: 1GB free storage → monitor vector count.
   - Render: 750 free hours/month → ensure UptimeRobot is configured.
   - Supabase: 500MB free DB → optimize queries and storage.
5. Deploy final backend to **Render** and verify all environment variables are set.
6. Verify **Vercel** deployment of the Lovable AI-generated frontend and connect it to the Render backend URL.
7. Run the **"2-Minute Live Demo" test:**
   - Execute `scripts/simulate_crash.py` to inject a fake anomalous log spike.
   - Verify the anomaly is detected and the LangGraph pipeline is triggered.
   - Verify the RCA report is generated with a suspected commit.
   - Verify the fix suggestion is generated.
   - Verify the Slack alert is received in the Slack channel.
   - Verify the post-mortem report is saved in the database.
   - Verify all data is visible on the frontend dashboard.
8. All checks pass → **Project is complete and live.**

**Deliverable:** A fully deployed, live, zero-cost AIOps platform accessible via a public URL with a 2-minute demo capability.

---

## 5. Final Outcome

Upon completion of all six phases, RootMind will be:

- **A Live Web Application** accessible via a public Vercel URL, featuring a beautiful React dashboard showing real-time incidents, agent status, root cause analysis results, fix suggestions, and post-mortem reports.
- **An Autonomous AI System** capable of detecting a production anomaly and completing the full diagnosis-fix-report cycle with zero human intervention.
- **A Slack-Integrated Alert Bot** that delivers instant, richly formatted, actionable incident alerts directly to a Slack channel.
- **A Portfolio Showpiece** with a live 2-minute demo: trigger a simulated crash → watch 4 AI agents work in sequence → receive a Slack alert → view the auto-generated fix and post-mortem on the dashboard.
- **A Zero-Cost System** where the entire production infrastructure runs on $0.00/month using strictly free-tier services.

---

## 6. Role of AI Models in This Project

| Model / Tool | Role | Agent(s) Used In |
|---|---|---|
| **Groq API (Llama 3 / Mixtral)** | Primary LLM brain. Processes structured context and generates human-readable reasoning, code patches, and professional reports. | RCA Agent, Fix Agent, Post-Mortem Agent |
| **Scikit-learn Isolation Forest** | Mathematical anomaly detector. Uses unsupervised ML to identify statistical deviations in log metric streams. No LLM involved. | Anomaly Agent |
| **Embedding Models (HuggingFace / Groq)** | Converts raw codebase text and incident records into high-dimensional vectors for semantic search. | RAG Pipeline, Memory Engine |
| **Qdrant Vector DB** | Stores and retrieves code vectors and incident memory. Enables the RAG pattern for context-aware LLM responses. | RAG Pipeline, Memory Engine |
| **LangGraph** | Orchestrates all agents as nodes in a stateful graph. Manages the flow, conditional routing, and state passing between agents. | graph.py (all agents) |

---

## 7. Strict Instructions for AI Models

> ATTENTION AI: You are acting as the **lead backend developer** for RootMind. You MUST adhere to the following rules **without exception** at all times.

1. **ZERO COST MANDATE:** Never suggest, implement, or rely on any paid API, paid model, or paid hosting service. Every service used must be on its free tier. If a free tier has rate limits, write code to gracefully handle those limits using caching, batching, retry logic with exponential backoff, or request queuing.

2. **STICK TO THE PLAN:** Do not hallucinate extra features, add unnecessary microservices, introduce new frameworks, or deviate from the 6-phase plan in any way. Build exactly and only what is outlined in this document.

3. **FRONTEND RESTRICTION:** Do NOT generate React, TypeScript, Vite, HTML, CSS, or any frontend-related code under any circumstances. The `frontend/` folder is strictly managed by Lovable AI. Direct 100% of code generation efforts toward the `backend/`, `agents/`, `models/`, `services/`, `utils/`, `scripts/`, and `tests/` directories only.

4. **FILE STRUCTURE COMPLIANCE:** Strictly follow the file structure defined in Section 3. Do not create files or folders outside of the defined architecture. Every new file must be placed exactly where the structure specifies.

5. **CODE QUALITY STANDARDS:** Write production-ready, modular, and thoroughly documented Python code. Every function must include: type hints on all parameters and return values, a docstring explaining purpose and parameters, and appropriate try/except error handling with informative error messages.

6. **PHASE DISCIPLINE:** Always be aware of which phase is currently active. Do not implement features belonging to a future phase. If asked to jump ahead, remind the user of the phase rule and complete the current phase first.

7. **CONTEXT AWARENESS:** Always remember the project name is **RootMind — Autonomous Multi-Agent AIOps Platform**. Keep the core business context in mind: reducing MTTR, minimizing downtime costs, and enabling autonomous incident resolution. All agent system prompts, variable names, and log messages should reflect this professional context.

8. **TESTING MANDATE:** Every agent and service implemented must have corresponding Pytest tests written in the `tests/` directory before that phase is considered complete. Do not mark a phase as done without its tests.

9. **ENVIRONMENT VARIABLE SAFETY:** Never hardcode API keys, secrets, database URLs, or any sensitive credentials in source code. All secrets must be loaded from environment variables via `app/config.py` using `python-dotenv`. Update `.env.example` with every new variable added.

10. **NO DEVIATION RESPONSE:** If a user instruction conflicts with any of the above rules, politely flag the conflict, explain which rule it violates, and propose a compliant alternative approach.

11. GIT & COMMIT DISCIPLINE: When asked to generate commits, strictly use the Conventional Commits format (e.g., feat(agent): implement Isolation Forest scoring, fix(api): resolve CORS error). Never generate lazy commit messages like "update code" or "fixed bug". Ensure .env and __pycache__ are never included in the commit.

---

## 8. Backend API Reference (For Lovable AI Frontend Handoff)

> This section is to be provided to Lovable AI in Phase 5 to generate the frontend dashboard.

**Base URL:** `https://rootmind-backend.onrender.com`
**Authentication:** API Key via `X-API-Key` header

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check — returns service status |
| `GET` | `/incidents` | List all incidents with pagination |
| `GET` | `/incidents/{id}` | Get a single incident by ID |
| `POST` | `/incidents` | Create a new incident record manually |
| `GET` | `/incidents/{id}/postmortem` | Get the auto-generated post-mortem report |
| `POST` | `/agents/run` | Trigger the full LangGraph pipeline with log data |
| `GET` | `/agents/status/{run_id}` | Get the status of an agent pipeline run |
| `POST` | `/webhooks/ingest` | Receive alerts from external tools (Prometheus, Datadog) |
| `POST` | `/webhooks/slack` | Receive Slack slash commands |