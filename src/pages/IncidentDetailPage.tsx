import { useEffect, useState } from 'react';
import { eventsForIncident } from '../data/events';
import { getDeployment } from '../data/deployments';
import { primaryIncidentId } from '../data/incidents';
import { logsForIncident } from '../data/logs';
import { deploy4821Diff, incidentDbEvidence, ordersErrorMetric, ordersLatencyMetric } from '../data/metrics';
import { LineChart } from '../components/charts/LineChart';
import { DepGraph } from '../components/charts/DepGraph';
import { AiInvestigation } from '../components/incidents/AiInvestigation';
import { LogPanel } from '../components/incidents/LogPanel';
import { Timeline } from '../components/incidents/Timeline';
import { WorkflowStepper } from '../components/incidents/WorkflowStepper';
import { Badge, severityBadge, statusBadgeClass, statusLabel } from '../components/ui/Badge';
import { incidentSections, useAppState } from '../hooks/useAppState';
import { formatTimer } from '../lib/format';
import type { IncidentSection } from '../types';

export function IncidentDetailPage() {
  const { selectedIncidentId, incidents, setView } = useAppState();
  const incident = incidents.find((item) => item.id === selectedIncidentId);
  const [section, setSection] = useState<IncidentSection>('sum');
  const [elapsed, setElapsed] = useState(incident?.elapsedSeconds ?? 0);

  useEffect(() => {
    setElapsed(incident?.elapsedSeconds ?? 0);
    setSection('sum');
  }, [incident?.id]);

  useEffect(() => {
    if (!incident || incident.status === 'resolved') return;
    const timer = window.setInterval(() => setElapsed((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, [incident?.id, incident?.status]);

  if (!incident) {
    return (
      <div className="card">
        <div className="empty-state">Incident not found.</div>
        <button className="btn btn-sm" type="button" onClick={() => setView('incidents')}>
          Back to incidents
        </button>
      </div>
    );
  }

  const events = eventsForIncident(incident.id);
  const logs = logsForIncident(incident.id);
  const flagged = getDeployment('dep-4821');
  const isPrimary = incident.id === primaryIncidentId;

  return (
    <>
      <button className="back-link" type="button" onClick={() => setView('dashboard')}>
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.3">
          <path d="M15 18l-6-6 6-6" />
        </svg>
        Back to overview
      </button>

      <div className="inc-header">
        <div className="inc-header-left">
          <div>
            <div className="badge-row">
              <Badge className={severityBadge(incident.severity)}>{incident.severity}</Badge>
              <Badge className={statusBadgeClass(incident.status)}>{statusLabel(incident.status)}</Badge>
            </div>
            <div className="inc-title-lg">
              {incident.id} — {incident.title}
            </div>
            <div className="inc-sub-lg">
              {isPrimary
                ? `${incident.serviceName} · orders-db · started ${incident.startedAt} · ${incident.trigger}`
                : `${incident.serviceName} · started ${incident.startedAt} · ${incident.trigger}`}
            </div>
          </div>
        </div>
        <div className="timer-box">
          <div className={`timer-val${incident.status === 'resolved' ? ' resolved' : ''}`}>{formatTimer(elapsed)}</div>
          <div className="timer-label">time to resolution</div>
        </div>
      </div>

      <WorkflowStepper current={incident.workflowStage} />

      <div className="section-nav">
        {incidentSections.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`section-tab${section === tab.id ? ' active' : ''}`}
            onClick={() => setSection(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {section === 'sum' ? (
        <div className="grid g-2">
          <div className="card">
            <div className="card-h">
              <div className="card-title">Timeline</div>
            </div>
            <Timeline events={events} />
          </div>
          <div className="card">
            <div className="card-h">
              <div className="card-title">Affected Services</div>
            </div>
            {incident.affectedServices.map((svc) => (
              <div className="gauge-row" key={svc.serviceId}>
                <div className="flex-center">
                  <span className={`dot dot-${svc.health}`} />
                  {svc.name}
                </div>
                <div className="inc-meta">{svc.metric}</div>
              </div>
            ))}
            <div className="audit-note">{incident.blastRadius}</div>
          </div>
        </div>
      ) : null}

      {section === 'metrics' ? (
        isPrimary ? (
          <>
            <div className="card">
              <div className="card-h">
                <div className="card-title">/orders — p95 Latency (ms)</div>
                <span className="badge badge-sev1">6.8s at peak</span>
              </div>
              <LineChart metric={ordersLatencyMetric} color="#F0465B" />
            </div>
            <div className="h-14" />
            <div className="card">
              <div className="card-h">
                <div className="card-title">/orders — 5xx Error Rate (%)</div>
                <span className="badge badge-sev1">22% at peak</span>
              </div>
              <LineChart metric={ordersErrorMetric} color="#F0465B" max={25} />
            </div>
          </>
        ) : (
          <div className="card empty-state">Metrics for this incident will appear when telemetry is attached.</div>
        )
      ) : null}

      {section === 'logs' ? (
        <div className="card">
          <div className="card-h">
            <div className="card-title">{incident.serviceName} · application logs</div>
            <div className="card-sub">{isPrimary ? '21:03:40 – 21:09:02 UTC' : 'correlated window'}</div>
          </div>
          <LogPanel entries={logs} />
        </div>
      ) : null}

      {section === 'deploy' ? (
        isPrimary && flagged ? (
          <div className="card">
            <div className="card-h">
              <div className="card-title">Deploy {flagged.version} — {flagged.serviceName}</div>
              <span className="badge badge-sev2">FLAGGED BY AI</span>
            </div>
            <div className="gauge-row">
              <div className="gauge-label">Author</div>
              <div className="inc-meta">{flagged.authorEmail}</div>
            </div>
            <div className="gauge-row">
              <div className="gauge-label">Deployed at</div>
              <div className="inc-meta">{flagged.deployedAt}</div>
            </div>
            <div className="gauge-row">
              <div className="gauge-label">Commit</div>
              <div className="inc-meta">
                {flagged.commit} — "{flagged.commitMessage}"
              </div>
            </div>
            <div className="gauge-row">
              <div className="gauge-label">Files changed</div>
              <div className="inc-meta">{flagged.filesChanged}</div>
            </div>
            <div className="mt-12">
              <div className="card-title mb-8">Diff excerpt — orders_repository.py</div>
              <div className="log-panel" style={{ maxHeight: 160 }}>
                {deploy4821Diff.map((line) => (
                  <div
                    className={`log-line ${line.startsWith('+') ? 'diff-add' : 'diff-meta'}`}
                    key={line}
                  >
                    {line}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="card empty-state">No flagged deployment correlated with this incident.</div>
        )
      ) : null}

      {section === 'db' ? (
        isPrimary ? (
          <div className="card">
            <div className="card-h">
              <div className="card-title">orders-db · postgres primary</div>
              <span className="badge badge-sev1">CONNECTION POOL EXHAUSTION</span>
            </div>
            <Gauge
              label="Connection pool util."
              pct={98}
              value={`${incidentDbEvidence.poolInUse}/${incidentDbEvidence.poolMax}`}
              color="var(--sev-1)"
            />
            <Gauge label="Avg query time (order_history)" pct={92} value="4.9s" color="var(--sev-1)" />
            <Gauge label="Rows scanned / query" pct={95} value={incidentDbEvidence.rowsScanned} color="var(--sev-1)" />
            <Gauge label="Queued connections" pct={80} value={String(incidentDbEvidence.queuedConnections)} color="var(--sev-2)" />
            <div className="mt-12">
              <div className="card-title mb-8">Top slow queries</div>
              <div className="log-panel" style={{ maxHeight: 140 }}>
                {incidentDbEvidence.slowQueries.map((query) => (
                  <div className="log-line" key={`${query.durationMs}-${query.sql}`}>
                    <span className="log-time">{query.durationMs}ms</span> {query.sql}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="card empty-state">No database evidence for this incident.</div>
        )
      ) : null}

      {section === 'dep' ? (
        <div className="card">
          <div className="card-h">
            <div className="card-title">Fault Propagation Path</div>
            <div className="card-sub">deploy → query time → pool exhaustion → latency → 5xx</div>
          </div>
          <DepGraph highlight={isPrimary} />
        </div>
      ) : null}

      {section === 'ai' ? <AiInvestigation incident={incident} /> : null}
    </>
  );
}

function Gauge({
  label,
  pct,
  value,
  color,
}: {
  label: string;
  pct: number;
  value: string;
  color: string;
}) {
  return (
    <div className="gauge-row">
      <div className="gauge-label">{label}</div>
      <div className="gauge-bar-track">
        <div className="gauge-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <div className="gauge-val" style={{ color }}>
        {value}
      </div>
    </div>
  );
}
