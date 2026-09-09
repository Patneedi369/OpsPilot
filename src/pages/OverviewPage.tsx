import { dashboardHealth, ordersLatencyMetric } from '../data/metrics';
import { aiInsights, dashboardMetrics } from '../data/platform';
import { deployments } from '../data/deployments';
import { LineChart } from '../components/charts/LineChart';
import { DepGraph } from '../components/charts/DepGraph';
import { IncidentTable } from '../components/incidents/IncidentTable';
import { DeployFeed } from '../components/incidents/DeployFeed';
import { useAppState } from '../hooks/useAppState';

export function OverviewPage() {
  const { incidents, openIncident } = useAppState();
  const recent = incidents.slice(0, 3);
  const m = dashboardMetrics;

  return (
    <>
      <div className="grid g-metrics mb-14">
        <div className="card metric-card">
          <div className="metric-top">
            <div className="card-title">System Health</div>
            <div className="metric-icon" style={{ background: 'var(--sev-2-dim)' }}>
              <svg viewBox="0 0 24 24" fill="none" stroke="#F5A524" strokeWidth="2">
                <path d="M12 2v20M2 12h20" />
              </svg>
            </div>
          </div>
          <div className="metric-val health-warn">
            {m.systemHealth}
            <span className="unit">/100</span>
          </div>
          <div className="metric-trend up-bad">
            ▼ {m.healthDelta} pts &nbsp;
            <span className="trend-muted">— {m.degradedServices} degraded service</span>
          </div>
        </div>
        <div className="card metric-card">
          <div className="metric-top">
            <div className="card-title">Active Incidents</div>
            <div className="metric-icon" style={{ background: 'var(--sev-1-dim)' }}>
              <svg viewBox="0 0 24 24" fill="none" stroke="#F0465B" strokeWidth="2">
                <path d="M12 9v4M12 17h.01M10.3 3.9L2.5 17.5a1.8 1.8 0 001.5 2.7h16a1.8 1.8 0 001.5-2.7L13.7 3.9a1.8 1.8 0 00-3.4 0z" />
              </svg>
            </div>
          </div>
          <div className="metric-val">{incidents.filter((item) => item.status !== 'resolved').length}</div>
          <div className="metric-trend trend-muted">
            {m.sevBreakdown.sev1} SEV-1 · {m.sevBreakdown.sev2} SEV-2 · {m.sevBreakdown.sev3} SEV-3
          </div>
        </div>
        <div className="card metric-card">
          <div className="metric-top">
            <div className="card-title">MTTR (7d avg)</div>
            <div className="metric-icon" style={{ background: 'var(--ok-dim)' }}>
              <svg viewBox="0 0 24 24" fill="none" stroke="#34D399" strokeWidth="2">
                <path d="M12 6v6l4 2" />
                <circle cx="12" cy="12" r="10" />
              </svg>
            </div>
          </div>
          <div className="metric-val">
            {m.mttrMinutes}
            <span className="unit">m</span>
          </div>
          <div className="metric-trend down-good">
            ▼ {m.mttrDeltaPct}% &nbsp;<span className="trend-muted">since AI remediation GA</span>
          </div>
        </div>
        <div className="card metric-card">
          <div className="metric-top">
            <div className="card-title">Deploys Today</div>
            <div className="metric-icon" style={{ background: 'var(--accent-ai-dim)' }}>
              <svg viewBox="0 0 24 24" fill="none" stroke="#9B87F5" strokeWidth="2">
                <rect x="3" y="4" width="18" height="16" rx="2" />
                <path d="M3 9h18" />
              </svg>
            </div>
          </div>
          <div className="metric-val">{m.deploysToday}</div>
          <div className="metric-trend trend-muted">
            {m.deployServices} services · {m.flaggedDeploys} flagged
          </div>
        </div>
      </div>

      <div className="grid g-2 mb-14">
        <div className="card">
          <div className="card-h">
            <div className="card-title">/orders API — Latency & Error Rate</div>
            <span className="badge badge-sev1">LIVE ANOMALY</span>
          </div>
          <div className="chart-legend">
            <div className="legend-item">
              <span className="legend-swatch" style={{ background: 'var(--accent-info)' }} />
              p95 latency (ms)
            </div>
            <div className="legend-item">
              <span className="legend-swatch" style={{ background: 'var(--sev-1)' }} />
              5xx error rate (%)
            </div>
          </div>
          <LineChart metric={ordersLatencyMetric} color="#4FC3F7" />
        </div>
        <div className="card">
          <div className="card-h">
            <div className="card-title">Database Health</div>
            <span className="badge badge-sev2">DEGRADED</span>
          </div>
          <Gauge label="Connection pool util." pct={dashboardHealth.connectionPoolUtilPct} value="96%" warn="crit" />
          <Gauge label="Avg query time" pct={78} value="640ms" warn="warn" />
          <Gauge
            label="Active connections"
            pct={88}
            value={`${dashboardHealth.activeConnections}/${dashboardHealth.maxConnections}`}
            warn="warn"
          />
          <Gauge label="Replication lag" pct={12} value="0.4s" warn="ok" />
          <Gauge label="Deadlocks / min" pct={6} value="0.2" warn="ok" />
        </div>
      </div>

      <div className="grid g-2 mb-14">
        <IncidentTable
          incidents={recent}
          onOpen={openIncident}
          title="Active & Recent Incidents"
          subtitle="Click a row to investigate"
        />
        <div className="card">
          <div className="card-h">
            <div className="card-title">AI Insights</div>
            <span className="badge badge-ai">LIVE</span>
          </div>
          {aiInsights.map((insight) => (
            <div className="insight-item" key={insight.id}>
              <div className="insight-ico">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2l2.4 7.4H22l-6 4.4 2.3 7.2L12 16.6 5.7 21l2.3-7.2-6-4.4h7.6z" />
                </svg>
              </div>
              <div>
                <div className="insight-text" dangerouslySetInnerHTML={{ __html: insight.text }} />
                <div className="insight-time">{insight.timeAgo}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid g-2">
        <div className="card">
          <div className="card-h">
            <div className="card-title">Service Dependency Health</div>
            <div className="card-sub">order-service → orders-db path highlighted</div>
          </div>
          <DepGraph highlight />
        </div>
        <div className="card">
          <div className="card-h">
            <div className="card-title">Recent Deployments</div>
          </div>
          <DeployFeed deployments={deployments} />
        </div>
      </div>
    </>
  );
}

function Gauge({
  label,
  pct,
  value,
  warn,
}: {
  label: string;
  pct: number;
  value: string;
  warn: 'ok' | 'warn' | 'crit';
}) {
  const color = warn === 'crit' ? 'var(--sev-1)' : warn === 'warn' ? 'var(--sev-2)' : 'var(--ok)';
  return (
    <div className="gauge-row">
      <div className="gauge-label">{label}</div>
      <div className="gauge-bar-track">
        <div className="gauge-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <div className="gauge-val" style={{ color: warn === 'ok' ? undefined : color }}>
        {value}
      </div>
    </div>
  );
}
