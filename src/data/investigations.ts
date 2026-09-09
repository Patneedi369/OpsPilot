import type { Investigation } from '../types';

export const mockInvestigation2043: Investigation = {
  id: 'inv-2043',
  incidentId: 'INC-2043',
  status: 'complete',
  model: 'claude-sonnet-4-6',
  evidence: [
    {
      id: 'evd-1',
      source: 'deployment',
      summary:
        'Deploy #4821 (21:04:12 UTC) added an order-history query filtering by customer_id and created_at',
    },
    {
      id: 'evd-2',
      source: 'database',
      summary:
        'No index exists on (customer_id, created_at); the new query triggers a full scan of 14.2M rows',
    },
    {
      id: 'evd-3',
      source: 'database',
      summary: 'order_history query time rose from 40ms to 4.9s immediately after the deploy',
    },
    {
      id: 'evd-4',
      source: 'database',
      summary:
        'orders-db connection pool climbed from 45/200 to 196/200 within 2 minutes as slow queries held connections open',
    },
    {
      id: 'evd-5',
      source: 'metrics',
      summary:
        'order-service p95 latency and 5xx rate spike onset (21:06) lags the deploy by under 2 minutes',
    },
  ],
  reasoning:
    'The new order-history query has no supporting index, forcing a full table scan on a 14M-row table. Each request now holds a database connection far longer than before, so the connection pool fills up and subsequent requests queue and time out, which surfaces as both latency and 5xx errors on order-service.',
  rootCause: {
    summary:
      'Deploy #4821 introduced an unindexed order-history query that causes full table scans, exhausting the orders-db connection pool and cascading into API latency and 5xx errors.',
    confidence: 92,
    expectedImpactIfUnresolved:
      'Checkout funnel degradation continues to worsen as pool exhaustion spreads to other order-service endpoints',
    affectedUsersEstimate: '~18% of active checkout sessions',
    model: 'claude-sonnet-4-6',
  },
  remediations: [
    {
      id: 'rem-rollback-4821',
      title: 'Rollback deploy #4821',
      description:
        'Revert order-service to the previous release, immediately removing the unindexed query.',
      risk: 'low',
      etaMinutes: 4,
      recommended: false,
      kind: 'rollback',
    },
    {
      id: 'rem-index-pool',
      title: 'Add composite index + raise pool ceiling',
      description:
        'Add an index on orders(customer_id, created_at) and temporarily raise the connection pool ceiling to relieve pressure while the index builds.',
      risk: 'medium',
      etaMinutes: 11,
      recommended: true,
      kind: 'infrastructure',
    },
  ],
};

export const mockInvestigation2041: Investigation = {
  id: 'inv-2041',
  incidentId: 'INC-2041',
  status: 'complete',
  model: 'claude-sonnet-4-6',
  evidence: [
    {
      id: 'evd-2041-1',
      source: 'metrics',
      summary: 'recs-cache hit-rate dropped from 94% to 41% beginning 20:13 UTC',
    },
    {
      id: 'evd-2041-2',
      source: 'metrics',
      summary: 'Eviction rate increased 4.1x with no corresponding code deploy',
    },
    {
      id: 'evd-2041-3',
      source: 'topology',
      summary: 'recs-service continues to serve traffic; degradation is isolated to cache capacity',
    },
  ],
  reasoning:
    'No application change correlates with the hit-rate drop. The eviction spike and memory pressure indicate the cache instance is undersized for current recommendation key cardinality.',
  rootCause: {
    summary: 'recs-cache is undersized for current key cardinality, causing LRU eviction and hit-rate collapse.',
    confidence: 81,
    expectedImpactIfUnresolved: 'Personalized recommendations remain degraded',
    affectedUsersEstimate: '~11% of recs traffic',
    model: 'claude-sonnet-4-6',
  },
  remediations: [
    {
      id: 'rem-scale-cache',
      title: 'Scale recs-cache instance',
      description: 'Increase recs-cache memory and watch eviction rate return to baseline.',
      risk: 'low',
      etaMinutes: 8,
      recommended: true,
      kind: 'infrastructure',
    },
    {
      id: 'rem-ttl-tune',
      title: 'Tighten recommendation key TTL',
      description: 'Reduce TTL to lower working set while a larger instance is provisioned.',
      risk: 'medium',
      etaMinutes: 15,
      recommended: false,
      kind: 'forward_fix',
    },
  ],
};

export const mockInvestigations: Record<string, Investigation> = {
  'INC-2043': mockInvestigation2043,
  'INC-2041': mockInvestigation2041,
};
