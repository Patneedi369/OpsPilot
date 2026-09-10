# OpsPilot — AI-Powered SRE & Incident Intelligence Platform

OpsPilot is an AI-powered SRE and Production Incident Intelligence platform that automates incident detection, signal correlation, root-cause investigation, human-in-the-loop remediation execution, and recovery verification.

---

## 🏗️ Architecture Overview

```
[ Telemetry Signals / Alerts ]
             │
             ▼
[ Detection & Signal Correlator ] ───► [ Persistent Incident Store ]
             │
             ▼
 [ LangGraph AI Investigator ] ───► [ PostgreSQL Checkpointer (HITL) ]
             │
             ▼
[ Human Approval / Interrupt ]
      │             │
   (Approve)     (Reject) ──► [ Incident Monitoring ]
      │
      ▼
[ Remediation Executor ] ──► [ Recovery Verifier ] ──► [ Recovered / Resolved ]
      │                             │
      └─────────────┬───────────────┘
                    ▼
           [ Immutable Audit Log ]
```

### Components
- **Frontend**: Vite + React + TypeScript single-page dashboard with role switcher and real-time investigation pipeline UI.
- **Backend API**: FastAPI framework providing REST endpoints, RBAC dependencies, correlation middleware, and health diagnostics.
- **AI Investigation Workflow**: LangGraph stategraph with PostgreSQL checkpointer thread isolation, multi-stage reasoning (Context Collector → Signal Correlator → Root Cause Analyst → Remediation Recommender).
- **Worker Process**: ARQ background worker executing async signal processing and scheduled detection tasks.
- **Database & Cache**: PostgreSQL (relational state & checkpointer) + Redis (cache, locks & job queue).

---

## 🔑 Demo Credentials

Development environment accounts seeded for testing:

| Username | Password | Role | Capabilities |
| :--- | :--- | :--- | :--- |
| `sre_user` | `sre_password` | **SRE** | View incidents, run AI investigations, approve/reject remediations, execute remediations |
| `lead_user` | `lead_password` | **Lead** | All SRE capabilities + access full immutable audit logs |
| `viewer_user` | `viewer_password` | **Viewer** | Read-only access across dashboard (mutations return HTTP 403 Forbidden) |

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` or set environment variables in your deployment:

```env
APP_NAME=opspilot-api
APP_ENV=development
LOG_LEVEL=INFO
SECRET_KEY=opspilot-secure-secret-key-2026-prod
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000

# Database & Cache (Docker internal host names or localhost:5433 / localhost:6379)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/opspilot
REDIS_URL=redis://localhost:6379/0

# Optional AI Provider (defaults to intelligent development fallback if blank)
ANTHROPIC_API_KEY=
AI_MODEL=claude-sonnet-4-6
AI_PROVIDER=anthropic
```

---

## 🚀 Getting Started

### Option 1: Full Docker Compose (Recommended)

Start the entire application stack (PostgreSQL, Redis, Backend API, Worker, and Frontend) with a single command:

```bash
docker compose up --build -d
```

Access the application:
- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **FastAPI API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

To view container logs:
```bash
docker compose logs -f
```

---

### Option 2: Local Development Workflow

#### 1. Start Infrastructure (PostgreSQL & Redis)
```bash
docker compose up -d postgres redis
```

#### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# Run database migrations & seed initial data
python -m alembic upgrade head

# Start API server
python -m uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend Setup
```bash
# In project root:
npm install
npm run dev
```

---

## 🎬 INC-2043 End-to-End Demo Walkthrough

The seeded scenario **INC-2043** demonstrates the full incident lifecycle:

1. **Telemetry & Signal Ingestion**:
   - Deployment `#4821` on `orders-service` triggers unindexed query execution (`(customer_id, created_at)` missing).
   - Slow DB query duration (>4500ms) drives DB connection pool exhaustion (>98%).
   - API p95 latency spikes to 4820ms and 5xx error rate breaches 18.4%.

2. **Automatic Detection & Correlation**:
   - Telemetry signals breach thresholds and automatically correlate into incident **INC-2043**.

3. **AI Investigation & Root Cause Analysis**:
   - LangGraph agent gathers metrics, deployment diffs, and database telemetry.
   - Diagnoses root cause: missing composite index + exhausted connection pool.
   - Recommends action: restore composite index and raise connection pool ceiling to 300.

4. **Human-in-the-Loop Approval**:
   - Incident pauses at `awaiting_approval` interrupt state in PostgreSQL checkpointer.
   - Operator clicks **Approve & Execute**.

5. **Execution & Recovery Verification**:
   - Executes remediation via safe abstraction.
   - Evaluates post-remediation signals: p95 latency drops to 240ms, 5xx rate normalizes to 0.1%, pool utilization relaxes to <50%.
   - Lifecycle transitions to **`recovered`**.

6. **Audit Trail**:
   - Complete immutable audit entry written to audit log with actor ID, timestamps, resource IDs, and execution metrics.

---

## 📡 Core API Endpoints

| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Public | System and infrastructure component health check |
| `POST` | `/api/v1/auth/login` | Public | Authenticates credentials and issues Bearer JWT token |
| `GET` | `/api/v1/incidents` | Public/Auth | Lists active and resolved incidents |
| `POST` | `/api/v1/incidents/{id}/investigate` | `SRE`, `Lead` | Triggers LangGraph AI investigation workflow |
| `GET` | `/api/v1/incidents/runs/{run_id}/approval` | Public/Auth | Retrieves current HITL approval state |
| `POST` | `/api/v1/incidents/runs/{run_id}/approve` | `SRE`, `Lead` | Approves remediation and triggers execution + verification |
| `POST` | `/api/v1/incidents/runs/{run_id}/reject` | `SRE`, `Lead` | Rejects remediation proposal |
| `POST` | `/api/v1/telemetry/signals` | `SRE`, `Lead` | Ingests telemetry metrics or event signals |
| `POST` | `/api/v1/telemetry/detect` | `SRE`, `Lead` | Triggers signal evaluation & correlation engine |
| `GET` | `/api/v1/audit/logs` | `SRE`, `Lead` | Queries immutable audit log history |
