import type { Service, ServiceEdge } from '../types';

export const services: Service[] = [
  { id: 'gateway', name: 'api-gateway', kind: 'gateway', health: 'ok' },
  { id: 'order-service', name: 'order-service', kind: 'service', health: 'crit', p95LatencyMs: 6800 },
  { id: 'checkout-service', name: 'checkout-service', kind: 'service', health: 'warn', p95LatencyMs: 1200 },
  { id: 'orders-db', name: 'orders-db', kind: 'datastore', health: 'crit', note: 'pool 96%' },
  { id: 'payments-service', name: 'payments-service', kind: 'service', health: 'ok' },
  { id: 'recs-cache', name: 'recs-cache', kind: 'cache', health: 'warn' },
  { id: 'auth-service', name: 'auth-service', kind: 'service', health: 'ok' },
  { id: 'recs-service', name: 'recs-service', kind: 'service', health: 'warn' },
  { id: 'search-service', name: 'search-service', kind: 'service', health: 'ok' },
];

export const topologyNodes = [
  { id: 'gateway', x: 60, y: 90, label: 'api-gateway', status: 'ok' as const },
  { id: 'order-service', x: 220, y: 40, label: 'order-service', status: 'crit' as const },
  { id: 'checkout-service', x: 220, y: 140, label: 'checkout-service', status: 'warn' as const },
  { id: 'orders-db', x: 400, y: 40, label: 'orders-db', status: 'crit' as const },
  { id: 'payments-service', x: 400, y: 140, label: 'payments-service', status: 'ok' as const },
  { id: 'recs-cache', x: 400, y: 190, label: 'recs-cache', status: 'warn' as const },
  { id: 'auth-service', x: 60, y: 190, label: 'auth-service', status: 'ok' as const },
];

export const topologyEdges: ServiceEdge[] = [
  { from: 'gateway', to: 'order-service', highlighted: true },
  { from: 'gateway', to: 'checkout-service', highlighted: false },
  { from: 'gateway', to: 'auth-service', highlighted: false },
  { from: 'order-service', to: 'orders-db', highlighted: true },
  { from: 'checkout-service', to: 'order-service', highlighted: true },
  { from: 'checkout-service', to: 'payments-service', highlighted: false },
  { from: 'checkout-service', to: 'recs-cache', highlighted: false },
];
