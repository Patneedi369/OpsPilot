from app.schemas.incident import Incident
from app.services.incident_catalog import INCIDENTS

EVENTS: list[dict[str, str]] = [
    {
        "id": "ev-2043-1",
        "incident_id": "INC-2043",
        "timestamp": "21:04:12",
        "title": "Deploy #4821 shipped",
        "description": "order-service — added order-history date-range filter, no index migration.",
        "type": "deploy",
    },
    {
        "id": "ev-2043-2",
        "incident_id": "INC-2043",
        "timestamp": "21:04:55",
        "title": "DB query time rising",
        "description": "order_history query avg jumps from 40ms → 1.2s on orders-db.",
        "type": "warn",
    },
    {
        "id": "ev-2043-3",
        "incident_id": "INC-2043",
        "timestamp": "21:05:40",
        "title": "Connection pool climbing",
        "description": "orders-db pool utilization crosses 85%; queued connections appear.",
        "type": "warn",
    },
    {
        "id": "ev-2043-4",
        "incident_id": "INC-2043",
        "timestamp": "21:06:10",
        "title": "Connection pool exhausted",
        "description": "Pool hits 196/200. New requests begin queuing on order-service.",
        "type": "crit",
    },
    {
        "id": "ev-2043-5",
        "incident_id": "INC-2043",
        "timestamp": "21:06:30",
        "title": "/orders latency spike",
        "description": "p95 latency crosses 5s, up from a 250ms baseline.",
        "type": "crit",
    },
    {
        "id": "ev-2043-6",
        "incident_id": "INC-2043",
        "timestamp": "21:06:45",
        "title": "5xx error rate spikes",
        "description": "Error rate reaches 22% as requests time out waiting on the pool.",
        "type": "crit",
    },
    {
        "id": "ev-2043-7",
        "incident_id": "INC-2043",
        "timestamp": "21:07:02",
        "title": "PagerDuty alert fired",
        "description": "SEV-1 auto-declared — on-call SRE paged.",
        "type": "crit",
    },
    {
        "id": "ev-2043-8",
        "incident_id": "INC-2043",
        "timestamp": "21:07:15",
        "title": "AI investigation opened",
        "description": "OpsPilot agent pipeline began evidence collection for INC-2043.",
        "type": "ai",
    },
    {
        "id": "ev-2041-1",
        "incident_id": "INC-2041",
        "timestamp": "20:13:02",
        "title": "Cache hit-rate drop detected",
        "description": "recs-cache hit-rate fell from 94% to 41% over 8 minutes.",
        "type": "warn",
    },
    {
        "id": "ev-2041-2",
        "incident_id": "INC-2041",
        "timestamp": "20:40:18",
        "title": "Eviction rate elevated",
        "description": "Redis eviction rate on recs-cache up 4.1x. No code change detected.",
        "type": "warn",
    },
    {
        "id": "ev-2041-3",
        "incident_id": "INC-2041",
        "timestamp": "20:41:10",
        "title": "AI investigation opened",
        "description": "OpsPilot correlated undersized instance capacity with eviction spike.",
        "type": "ai",
    },
    {
        "id": "ev-2038-1",
        "incident_id": "INC-2038",
        "timestamp": "18:54:10",
        "title": "Token refresh latency elevated",
        "description": "auth-service p95 crossed 800ms versus 180ms baseline.",
        "type": "warn",
    },
    {
        "id": "ev-2038-2",
        "incident_id": "INC-2038",
        "timestamp": "19:03:20",
        "title": "Remediation executed",
        "description": "auth-token-cache restarted with 0 errors.",
        "type": "ok",
    },
    {
        "id": "ev-2038-3",
        "incident_id": "INC-2038",
        "timestamp": "19:12:40",
        "title": "Incident verified resolved",
        "description": "Token refresh p95 back within 180ms baseline for 15 consecutive minutes.",
        "type": "ok",
    },
]

LOGS: list[dict[str, str]] = [
    {"id": "log-1", "incident_id": "INC-2043", "timestamp": "21:04:12.019", "level": "INFO", "service": "order-service", "message": "deploy complete: version=4821 commit=a3f9d2e"},
    {"id": "log-2", "incident_id": "INC-2043", "timestamp": "21:04:56.221", "level": "WARN", "service": "order-service", "message": "slow query detected: order_history_query took 1204ms"},
    {"id": "log-3", "incident_id": "INC-2043", "timestamp": "21:05:41.884", "level": "WARN", "service": "orders-db", "message": "connection pool utilization=86% (threshold=80%)"},
    {"id": "log-4", "incident_id": "INC-2043", "timestamp": "21:06:10.442", "level": "ERROR", "service": "orders-db", "message": "connection pool exhausted: 196/200 in use, 41 queued"},
    {"id": "log-5", "incident_id": "INC-2043", "timestamp": "21:06:12.009", "level": "ERROR", "service": "order-service", "message": "DB acquire timeout after 5000ms — GET /orders?customer_id=88213"},
    {"id": "log-6", "incident_id": "INC-2043", "timestamp": "21:06:14.552", "level": "ERROR", "service": "order-service", "message": "DB acquire timeout after 5000ms — GET /orders?customer_id=44120"},
    {"id": "log-7", "incident_id": "INC-2043", "timestamp": "21:06:30.771", "level": "WARN", "service": "order-service", "message": "p95 latency=5230ms (baseline=250ms)"},
    {"id": "log-8", "incident_id": "INC-2043", "timestamp": "21:06:45.113", "level": "ERROR", "service": "order-service", "message": "HTTP 503 returned — upstream orders-db unavailable"},
    {"id": "log-9", "incident_id": "INC-2043", "timestamp": "21:07:02.940", "level": "ERROR", "service": "alertmanager", "message": "SEV-1 declared: order-service 5xx_rate > 15% for 60s"},
    {"id": "log-10", "incident_id": "INC-2043", "timestamp": "21:07:15.300", "level": "INFO", "service": "opspilot-agent", "message": "evidence collection started for INC-2043"},
    {"id": "log-2041-1", "incident_id": "INC-2041", "timestamp": "20:13:02.110", "level": "WARN", "service": "recs-cache", "message": "hit-rate=71% (baseline=94%)"},
    {"id": "log-2041-2", "incident_id": "INC-2041", "timestamp": "20:40:18.441", "level": "WARN", "service": "recs-cache", "message": "eviction_rate=4.1x baseline; maxmemory-policy=allkeys-lru"},
    {"id": "log-2041-3", "incident_id": "INC-2041", "timestamp": "20:41:10.002", "level": "INFO", "service": "opspilot-agent", "message": "INC-2041 opened — Redis eviction anomaly on recs-cache"},
    {"id": "log-2038-1", "incident_id": "INC-2038", "timestamp": "18:54:10.220", "level": "WARN", "service": "auth-service", "message": "token refresh p95=812ms (baseline=180ms)"},
    {"id": "log-2038-2", "incident_id": "INC-2038", "timestamp": "19:03:20.014", "level": "INFO", "service": "opspilot-agent", "message": "remediation executed — auth-token-cache restarted, 0 errors"},
    {"id": "log-2038-3", "incident_id": "INC-2038", "timestamp": "19:12:40.880", "level": "INFO", "service": "opspilot-agent", "message": "INC-2038 auto-verified resolved (15min stable window)"},
]

DEPLOYMENTS: list[dict[str, str]] = [
    {"id": "dep-4821", "version": "#4821", "service_id": "order-service", "service_name": "order-service", "author": "r.patel", "author_email": "r.patel@company.com", "deployed_at": "21:04:12 UTC", "time_label": "21:04", "status": "flagged", "commit": "a3f9d2e", "commit_message": "Add order history filter by date range", "files_changed": "3 files, +48 −6"},
    {"id": "dep-4820", "version": "#4820", "service_id": "search-service", "service_name": "search-service", "author": "k.wu", "author_email": "k.wu@company.com", "deployed_at": "19:55:00 UTC", "time_label": "19:55", "status": "healthy", "commit": "b81c004", "commit_message": "Tune search indexer batch size", "files_changed": "2 files, +12 −3"},
    {"id": "dep-4819", "version": "#4819", "service_id": "auth-service", "service_name": "auth-service", "author": "a.chen", "author_email": "a.chen@company.com", "deployed_at": "18:30:00 UTC", "time_label": "18:30", "status": "healthy", "commit": "c12ee90", "commit_message": "Reduce token-cache stampede", "files_changed": "4 files, +31 −9"},
    {"id": "dep-4818", "version": "#4818", "service_id": "payments-service", "service_name": "payments-service", "author": "r.patel", "author_email": "r.patel@company.com", "deployed_at": "16:12:00 UTC", "time_label": "16:12", "status": "healthy", "commit": "d44aa11", "commit_message": "Webhook retry backoff", "files_changed": "1 file, +8 −1"},
    {"id": "dep-4817", "version": "#4817", "service_id": "recs-service", "service_name": "recs-service", "author": "j.moreno", "author_email": "j.moreno@company.com", "deployed_at": "14:02:00 UTC", "time_label": "14:02", "status": "healthy", "commit": "e90bb22", "commit_message": "Feature flag for recs ranking v2", "files_changed": "5 files, +64 −11"},
]


def incident_rows() -> list[Incident]:
    return list(INCIDENTS)
