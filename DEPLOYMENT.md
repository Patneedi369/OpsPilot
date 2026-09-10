# OpsPilot Production Cloud Deployment Guide

This document outlines the deployment strategy, environment requirements, health probing, migration process, and rollback guidelines for deploying OpsPilot to a production cloud container environment (e.g. AWS ECS / AWS App Runner / Render / DigitalOcean App Platform).

---

## 🏗️ Architecture & Component Topology

```
                  ┌────────────────────────┐
                  │   Cloud Load Balancer  │
                  └───────────┬────────────┘
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
┌────────────────────────┐        ┌────────────────────────┐
│  Frontend (Nginx Container)│     │  Backend API (FastAPI) │
└────────────────────────┘        └───────────┬────────────┘
                                              │
                     ┌────────────────────────┼────────────────────────┐
                     ▼                        ▼                        ▼
        ┌────────────────────────┐┌───────────────────────┐┌────────────────────────┐
        │ Managed PostgreSQL     ││ Managed Redis         ││ ARQ Worker Container   │
        └────────────────────────┘└───────────────────────┘└────────────────────────┘
```

### Components
1. **Frontend Container**: Nginx serving static React bundle, proxying `/api/` traffic to the Backend API.
2. **Backend API Container**: FastAPI process handling REST & SSE endpoints (`/api/v1/health`, `/api/v1/incidents`, `/api/v1/telemetry`, `/api/v1/audit`).
3. **Worker Container**: ARQ background process processing async signals and periodic detection tasks (`python -m app.workers.run_stub`).
4. **PostgreSQL 16**: Managed PostgreSQL database instance (Amazon RDS / GCP Cloud SQL / DigitalOcean Postgres).
5. **Redis 7**: Managed Redis instance (Amazon ElastiCache / Redis Cloud).

---

## 🔑 Environment Variables

Specify the following environment variables in your container runner platform:

| Variable | Recommended Production Value | Description |
| :--- | :--- | :--- |
| `APP_NAME` | `opspilot-api` | Application name identifier |
| `APP_ENV` | `production` | Environment indicator |
| `LOG_LEVEL` | `INFO` | Log verbosity level |
| `SECRET_KEY` | *(Set strong random 64-char string)* | JWT HMAC signature key |
| `JWT_ALGORITHM` | `HS256` | Token signing algorithm |
| `CORS_ORIGINS` | `https://opspilot.yourdomain.com` | Allowed CORS origins (comma-separated) |
| `DATABASE_URL` | `postgresql+asyncpg://<user>:<password>@<db-host>:5432/opspilot` | Managed PostgreSQL connection URI |
| `REDIS_URL` | `redis://<redis-host>:6379/0` | Managed Redis connection URI |
| `ANTHROPIC_API_KEY` | *(Optional)* | Anthropic Claude API Key for production AI reasoning |
| `AI_PROVIDER` | `anthropic` or `fallback` | Provider selection |

---

## 🗄️ Database Migration & Startup Strategy

1. **Database Provisioning**: Ensure PostgreSQL database `opspilot` is provisioned and reachable.
2. **Migration Command**: Run database migrations before container launch or as a pre-deploy release task:
   ```bash
   python -m alembic upgrade head
   ```
3. **Automated Container Entrypoint**: The default `backend/Dockerfile` entrypoint executes `alembic upgrade head` prior to starting Uvicorn, guaranteeing schema synchronization on every deployment.

---

## 🩺 Health Checks & Readiness Probes

Configure container orchestrator probes against these endpoints:

| Endpoint | Probe Type | Expected Status | Description |
| :--- | :--- | :--- | :--- |
| `/api/v1/health` | Liveness / Readiness | HTTP 200 OK | Verifies API process, PostgreSQL, and Redis connectivity |
| `/api/v1/health/readiness` | Readiness Probe | HTTP 200 OK | Ensures DB `SELECT 1` succeeds before routing load balancer traffic |

---

## 🔄 Rollback Considerations

1. **Database Schema Compatibility**: Alembic migrations are written additively (`0001` through `0004`).
2. **Rollback Command**: If a release must be rolled back:
   ```bash
   python -m alembic downgrade -1
   ```
3. **Container Rollback**: Revert load balancer task definitions to the previous tagged container commit hash (e.g. `opspilot-backend:v1.2.0`).
