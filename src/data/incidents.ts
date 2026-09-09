import type { Incident } from '../types';

export const incidents: Incident[] = [
  {
    id: 'INC-2043',
    title: '/orders API latency spike (6.8s p95)',
    severity: 'SEV-1',
    status: 'investigating',
    workflowStage: 'investigation',
    serviceId: 'order-service',
    serviceName: 'order-service',
    startedAt: '21:04:12 UTC',
    durationLabel: '14m',
    elapsedSeconds: 14 * 60 + 22,
    trigger: 'triggered by deploy #4821',
    affectedServices: [
      { serviceId: 'order-service', name: 'order-service', health: 'crit', metric: 'p95 6.8s' },
      { serviceId: 'orders-db', name: 'orders-db', health: 'crit', metric: 'pool 96%' },
      { serviceId: 'checkout-service', name: 'checkout-service', health: 'warn', metric: 'p95 1.2s' },
      { serviceId: 'payments-service', name: 'payments-service', health: 'ok', metric: 'nominal' },
    ],
    blastRadius: '4 services · 1 datastore · blast radius: checkout funnel',
  },
  {
    id: 'INC-2041',
    title: 'Redis cache hit-rate drop — recommendations',
    severity: 'SEV-2',
    status: 'monitoring',
    workflowStage: 'verification',
    serviceId: 'recs-service',
    serviceName: 'recs-service',
    startedAt: '20:13:00 UTC',
    durationLabel: '51m',
    elapsedSeconds: 51 * 60,
    trigger: 'Redis eviction anomaly on recs-cache',
    affectedServices: [
      { serviceId: 'recs-service', name: 'recs-service', health: 'warn', metric: 'hit-rate 41%' },
      { serviceId: 'recs-cache', name: 'recs-cache', health: 'warn', metric: 'eviction 4.1x' },
    ],
    blastRadius: 'recommendations surface · degraded personalization',
  },
  {
    id: 'INC-2038',
    title: 'Elevated auth token refresh latency',
    severity: 'SEV-3',
    status: 'resolved',
    workflowStage: 'resolution',
    serviceId: 'auth-service',
    serviceName: 'auth-service',
    startedAt: '18:54:00 UTC',
    durationLabel: '2h 10m',
    elapsedSeconds: 2 * 3600 + 10 * 60,
    trigger: 'auth-token-cache saturation',
    affectedServices: [
      { serviceId: 'auth-service', name: 'auth-service', health: 'ok', metric: 'p95 168ms' },
    ],
    blastRadius: 'token refresh path · resolved',
  },
  {
    id: 'INC-2029',
    title: 'Payment webhook retries exceeding threshold',
    severity: 'SEV-3',
    status: 'resolved',
    workflowStage: 'resolution',
    serviceId: 'payments-service',
    serviceName: 'payments-service',
    startedAt: '1d ago',
    durationLabel: '1d ago',
    elapsedSeconds: 86400,
    trigger: 'downstream processor timeout burst',
    affectedServices: [
      { serviceId: 'payments-service', name: 'payments-service', health: 'ok', metric: 'nominal' },
    ],
    blastRadius: 'webhook retries · resolved',
  },
  {
    id: 'INC-2011',
    title: 'Search indexing lag on catalog updates',
    severity: 'SEV-3',
    status: 'resolved',
    workflowStage: 'resolution',
    serviceId: 'search-service',
    serviceName: 'search-service',
    startedAt: '3d ago',
    durationLabel: '3d ago',
    elapsedSeconds: 3 * 86400,
    trigger: 'indexer worker backlog',
    affectedServices: [
      { serviceId: 'search-service', name: 'search-service', health: 'ok', metric: 'lag 2s' },
    ],
    blastRadius: 'catalog search freshness · resolved',
  },
];

export const primaryIncidentId = 'INC-2043';

export function getIncident(id: string): Incident | undefined {
  return incidents.find((incident) => incident.id === id);
}
