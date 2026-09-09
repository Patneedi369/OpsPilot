import type { Metric } from '../types';

export const timeLabels = [
  '20:59',
  '21:00',
  '21:01',
  '21:02',
  '21:03',
  '21:04',
  '21:05',
  '21:06',
  '21:07',
  '21:08',
  '21:09',
  '21:10',
  '21:11',
  '21:12',
  '21:13',
  '21:14',
  '21:15',
  '21:16',
  '21:17',
  '21:18',
  '21:19',
  '21:20',
  '21:21',
  '21:22',
  '21:23',
];

const latencyValues = [
  260, 255, 270, 248, 265, 258, 272, 690, 2100, 3800, 5200, 6100, 6800, 6500, 6200, 5900, 5400, 4800, 4100, 3200, 2400, 1600, 1100, 780, 520,
];

const errorValues = [
  0.2, 0.1, 0.3, 0.2, 0.2, 0.1, 0.3, 1.8, 5.2, 9.1, 13.4, 17.2, 22.0, 20.5, 19.1, 17.8, 15.2, 12.4, 9.8, 6.5, 4.1, 2.2, 1.1, 0.5, 0.2,
];

function toSeries(values: number[]): Metric['series'] {
  return values.map((value, index) => ({ timestamp: timeLabels[index], value }));
}

export const ordersLatencyMetric: Metric = {
  id: 'orders-p95',
  name: '/orders p95 latency',
  unit: 'ms',
  series: toSeries(latencyValues),
  markerIndex: 5,
};

export const ordersErrorMetric: Metric = {
  id: 'orders-5xx',
  name: '/orders 5xx error rate',
  unit: '%',
  series: toSeries(errorValues),
  markerIndex: 5,
};

export const dashboardHealth = {
  connectionPoolUtilPct: 96,
  avgQueryTimeMs: 640,
  activeConnections: 177,
  maxConnections: 200,
  replicationLagSec: 0.4,
  deadlocksPerMin: 0.2,
};

export const incidentDbEvidence = {
  poolInUse: 196,
  poolMax: 200,
  avgQueryTimeMs: 4900,
  rowsScanned: '14.2M',
  queuedConnections: 41,
  slowQueries: [
    {
      durationMs: 4923,
      sql: 'SELECT * FROM orders WHERE customer_id=$1 AND created_at BETWEEN $2 AND $3 ORDER BY created_at DESC',
    },
    {
      durationMs: 4710,
      sql: 'SELECT * FROM orders WHERE customer_id=$1 AND created_at BETWEEN $2 AND $3 ORDER BY created_at DESC',
    },
    {
      durationMs: 210,
      sql: 'SELECT * FROM order_items WHERE order_id=$1',
    },
  ],
};

export const deploy4821Diff = [
  '@@ order_history_query()',
  '+ SELECT * FROM orders',
  '+ WHERE customer_id = %s AND created_at BETWEEN %s AND %s',
  '+ ORDER BY created_at DESC',
  '  -- no index on (customer_id, created_at)',
  '  -- table scan on orders (14.2M rows)',
];
