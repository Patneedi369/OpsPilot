import type { LogEntry } from '../types';

export const logEntries: LogEntry[] = [
  {
    id: 'log-1',
    timestamp: '21:04:12.019',
    level: 'INFO',
    service: 'order-service',
    message: 'deploy complete: version=4821 commit=a3f9d2e',
  },
  {
    id: 'log-2',
    timestamp: '21:04:56.221',
    level: 'WARN',
    service: 'order-service',
    message: 'slow query detected: order_history_query took 1204ms',
  },
  {
    id: 'log-3',
    timestamp: '21:05:41.884',
    level: 'WARN',
    service: 'orders-db',
    message: 'connection pool utilization=86% (threshold=80%)',
  },
  {
    id: 'log-4',
    timestamp: '21:06:10.442',
    level: 'ERROR',
    service: 'orders-db',
    message: 'connection pool exhausted: 196/200 in use, 41 queued',
  },
  {
    id: 'log-5',
    timestamp: '21:06:12.009',
    level: 'ERROR',
    service: 'order-service',
    message: 'DB acquire timeout after 5000ms — GET /orders?customer_id=88213',
  },
  {
    id: 'log-6',
    timestamp: '21:06:14.552',
    level: 'ERROR',
    service: 'order-service',
    message: 'DB acquire timeout after 5000ms — GET /orders?customer_id=44120',
  },
  {
    id: 'log-7',
    timestamp: '21:06:30.771',
    level: 'WARN',
    service: 'order-service',
    message: 'p95 latency=5230ms (baseline=250ms)',
  },
  {
    id: 'log-8',
    timestamp: '21:06:45.113',
    level: 'ERROR',
    service: 'order-service',
    message: 'HTTP 503 returned — upstream orders-db unavailable',
  },
  {
    id: 'log-9',
    timestamp: '21:07:02.940',
    level: 'ERROR',
    service: 'alertmanager',
    message: 'SEV-1 declared: order-service 5xx_rate > 15% for 60s',
  },
  {
    id: 'log-10',
    timestamp: '21:07:15.300',
    level: 'INFO',
    service: 'opspilot-agent',
    message: 'evidence collection started for INC-2043',
  },
];

export const logsByIncident: Record<string, LogEntry[]> = {
  'INC-2043': logEntries,
  'INC-2041': [
    {
      id: 'log-2041-1',
      timestamp: '20:13:02.110',
      level: 'WARN',
      service: 'recs-cache',
      message: 'hit-rate=71% (baseline=94%)',
    },
    {
      id: 'log-2041-2',
      timestamp: '20:40:18.441',
      level: 'WARN',
      service: 'recs-cache',
      message: 'eviction_rate=4.1x baseline; maxmemory-policy=allkeys-lru',
    },
    {
      id: 'log-2041-3',
      timestamp: '20:41:10.002',
      level: 'INFO',
      service: 'opspilot-agent',
      message: 'INC-2041 opened — Redis eviction anomaly on recs-cache',
    },
  ],
  'INC-2038': [
    {
      id: 'log-2038-1',
      timestamp: '18:54:10.220',
      level: 'WARN',
      service: 'auth-service',
      message: 'token refresh p95=812ms (baseline=180ms)',
    },
    {
      id: 'log-2038-2',
      timestamp: '19:03:20.014',
      level: 'INFO',
      service: 'opspilot-agent',
      message: 'remediation executed — auth-token-cache restarted, 0 errors',
    },
    {
      id: 'log-2038-3',
      timestamp: '19:12:40.880',
      level: 'INFO',
      service: 'opspilot-agent',
      message: 'INC-2038 auto-verified resolved (15min stable window)',
    },
  ],
};

export function logsForIncident(incidentId: string): LogEntry[] {
  return logsByIncident[incidentId] ?? [];
}
