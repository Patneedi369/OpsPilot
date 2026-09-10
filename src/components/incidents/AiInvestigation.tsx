import { useMemo, useState } from 'react';
import type { Incident, Investigation, RemediationAction, WorkflowStage } from '../../types';
import { investigationService, investigateEndpoint } from '../../services/investigation';
import { approvalHint, canApproveRemediation, canRunInvestigation } from '../../lib/permissions';
import { utcNowLabel } from '../../lib/format';
import { useAppState } from '../../hooks/useAppState';
import { useIncidentStream, type IncidentSseEvent } from '../../hooks/useIncidentStream';

interface AiInvestigationProps {
  incident: Incident;
}

export function AiInvestigation({ incident }: AiInvestigationProps) {
  const { role, investigations, setInvestigation, upsertIncident, appendAudit } = useAppState();
  const investigation = investigations[incident.id];
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [rejected, setRejected] = useState(false);
  const [execIndex, setExecIndex] = useState(-1);
  const [executing, setExecuting] = useState(false);
  const [verified, setVerified] = useState(incident.status === 'resolved');

  useIncidentStream(incident.id, (evt: IncidentSseEvent) => {
    if (evt.type === 'remediation_executing') {
      setExecuting(true);
      setExecIndex(1);
      upsertIncident(incident.id, { status: 'executing', workflowStage: 'execution' });
    } else if (evt.type === 'remediation_completed' || evt.type === 'recovery_verification_started') {
      setExecIndex(3);
      upsertIncident(incident.id, { status: 'executing', workflowStage: 'verification' });
    } else if (evt.type === 'incident_recovered') {
      setExecIndex(4);
      setVerified(true);
      setExecuting(false);
      upsertIncident(incident.id, { status: 'resolved', workflowStage: 'resolution' });
    } else if (evt.type === 'remediation_rejected') {
      setRejected(true);
      setExecuting(false);
    }
  });

  const selected = useMemo(() => {
    if (!investigation) return undefined;
    return (
      investigation.remediations.find((action) => action.id === selectedId) ??
      investigation.remediations.find((action) => action.recommended) ??
      investigation.remediations[0]
    );
  }, [investigation, selectedId]);

  async function runInvestigation() {
    if (!canRunInvestigation(role)) return;
    setRunning(true);
    setError(null);
    setRejected(false);
    setVerified(false);
    setExecIndex(-1);
    upsertIncident(incident.id, { status: 'investigating', workflowStage: 'investigation' });
    try {
      const result = await investigationService.investigate(incident.id);
      setInvestigation(incident.id, result);
      const recommended = result.remediations.find((action) => action.recommended) ?? result.remediations[0];
      setSelectedId(recommended?.id ?? null);
      upsertIncident(incident.id, {
        status: 'awaiting_approval',
        workflowStage: 'remediation_proposal',
      });
      appendAudit(
        `opspilot-agent: investigation complete for ${incident.id} (mock POST ${investigateEndpoint(incident.id)})`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Investigation failed');
    } finally {
      setRunning(false);
    }
  }

  function updateStage(stage: WorkflowStage, status: Incident['status']) {
    upsertIncident(incident.id, { workflowStage: stage, status });
  }

  async function approve() {
    if (!selected || !canApproveRemediation(role, selected)) return;
    setExecuting(true);
    updateStage('human_approval', 'executing');
    appendAudit(`${role}: approved remediation "${selected.title}" for ${incident.id}`);
    const steps = 4;
    for (let i = 0; i < steps; i += 1) {
      setExecIndex(i);
      updateStage(i < 2 ? 'execution' : 'verification', 'executing');
      await new Promise((resolve) => setTimeout(resolve, 700));
    }
    setExecIndex(steps);
    setVerified(true);
    setExecuting(false);
    upsertIncident(incident.id, {
      status: 'resolved',
      workflowStage: 'resolution',
      durationLabel: 'resolved',
    });
    appendAudit(
      `opspilot-agent: remediation executed and verified for ${incident.id} — action_id rem-8842, approved_by: ${role}, executed_at: ${utcNowLabel()} UTC`,
    );
  }

  function reject() {
    setRejected(true);
    updateStage('human_approval', 'monitoring');
    appendAudit(`${role}: rejected proposed remediation for ${incident.id}`);
  }

  const canApprove = selected ? canApproveRemediation(role, selected) : false;

  return (
    <div className="ai-panel">
      <div className="ai-panel-head">
        <div className="ai-panel-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2l2.4 7.4H22l-6 4.4 2.3 7.2L12 16.6 5.7 21l2.3-7.2-6-4.4h7.6z" />
          </svg>
          AI Root-Cause Investigation
        </div>
        <button
          className="btn btn-primary btn-sm"
          type="button"
          disabled={running || !canRunInvestigation(role)}
          onClick={() => void runInvestigation()}
        >
          {running ? 'Investigating…' : investigation ? 'Re-run investigation' : 'Run investigation'}
        </button>
      </div>
      <div className="ai-body">
        {!canRunInvestigation(role) && !investigation ? (
          <div className="card-sub" style={{ fontSize: 12 }}>
            Engineering Manager can review evidence but cannot start an AI investigation.
          </div>
        ) : null}
        {error ? <div className="error-text">{error}</div> : null}
        {running ? <InvestigationSkeleton /> : null}
        {!running && !investigation && !error ? (
          <div className="card-sub" style={{ fontSize: 12 }}>
            Not yet run for this incident. Click <b>Run investigation</b> to have OpsPilot analyze evidence and propose a
            root cause. The frontend calls a service abstraction that will later POST{' '}
            <code>{investigateEndpoint(incident.id)}</code>.
          </div>
        ) : null}
        {!running && investigation ? (
          <InvestigationResult
            investigation={investigation}
            selected={selected}
            rejected={rejected}
            executing={executing}
            execIndex={execIndex}
            verified={verified}
            canApprove={canApprove}
            hint={approvalHint(role, selected)}
            onSelect={setSelectedId}
            onApprove={() => void approve()}
            onReject={reject}
          />
        ) : null}
      </div>
    </div>
  );
}

function InvestigationSkeleton() {
  return (
    <>
      <div className="ai-step">
        <div className="ai-step-head">
          <div className="ai-step-num">1</div>
          <div className="ai-step-title">Collecting evidence</div>
        </div>
        <div className="skeleton sk-line" style={{ width: '92%' }} />
        <div className="skeleton sk-line" style={{ width: '78%' }} />
        <div className="skeleton sk-line" style={{ width: '85%' }} />
      </div>
      <div className="ai-step">
        <div className="ai-step-head">
          <div className="ai-step-num">2</div>
          <div className="ai-step-title">Correlating signals & reasoning</div>
        </div>
        <div className="skeleton sk-line" style={{ width: '96%' }} />
        <div className="skeleton sk-line" style={{ width: '70%' }} />
      </div>
      <div className="ai-step">
        <div className="ai-step-head">
          <div className="ai-step-num">3</div>
          <div className="ai-step-title">Determining root cause</div>
        </div>
        <div className="skeleton sk-line" style={{ width: '60%' }} />
      </div>
    </>
  );
}

interface ResultProps {
  investigation: Investigation;
  selected?: RemediationAction;
  rejected: boolean;
  executing: boolean;
  execIndex: number;
  verified: boolean;
  canApprove: boolean;
  hint: string;
  onSelect: (id: string) => void;
  onApprove: () => void;
  onReject: () => void;
}

function InvestigationResult({
  investigation,
  selected,
  rejected,
  executing,
  execIndex,
  verified,
  canApprove,
  hint,
  onSelect,
  onApprove,
  onReject,
}: ResultProps) {
  const root = investigation.rootCause;
  const conf = rootCauseColor(root?.confidence ?? 0);
  const circumference = 2 * Math.PI * 27;
  const steps = selected
    ? [
        { name: 'Validating remediation plan', detail: selected.title },
        { name: 'Acquiring execution lock', detail: 'orders-db · order-service' },
        { name: `Executing: ${selected.title}`, detail: selected.description },
        { name: 'Monitoring post-change metrics', detail: 'watching p95 latency & 5xx rate' },
      ]
    : [];

  return (
    <>
      <div className="ai-step">
        <div className="ai-step-head">
          <div className="ai-step-num">1</div>
          <div className="ai-step-title">Evidence</div>
        </div>
        <ul className="evidence-list">
          {investigation.evidence.map((item) => (
            <li className="evidence-item" key={item.id}>
              {item.summary}
            </li>
          ))}
        </ul>
      </div>
      <div className="ai-step">
        <div className="ai-step-head">
          <div className="ai-step-num">2</div>
          <div className="ai-step-title">Reasoning</div>
        </div>
        <div className="reasoning-text">{investigation.reasoning}</div>
      </div>
      {root ? (
        <>
          <div className="ai-step">
            <div className="ai-step-head">
              <div className="ai-step-num">3</div>
              <div className="ai-step-title">Root cause</div>
            </div>
            <div className="root-cause-box">
              <div className="root-cause-label">Diagnosed root cause</div>
              <div className="root-cause-text">{root.summary}</div>
            </div>
          </div>
          <div className="ai-step">
            <div className="ai-step-head">
              <div className="ai-step-num">4</div>
              <div className="ai-step-title">Confidence & expected impact</div>
            </div>
            <div className="confidence-wrap">
              <div className="confidence-ring">
                <svg width="64" height="64" viewBox="0 0 64 64">
                  <circle cx="32" cy="32" r="27" fill="none" stroke="#212836" strokeWidth="6" />
                  <circle
                    cx="32"
                    cy="32"
                    r="27"
                    fill="none"
                    stroke={conf}
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={circumference * (1 - root.confidence / 100)}
                    transform="rotate(-90 32 32)"
                  />
                </svg>
                <div className="confidence-num" style={{ color: conf }}>
                  {root.confidence}%
                </div>
              </div>
              <div className="impact-grid" style={{ flex: 1 }}>
                <div className="impact-box">
                  <div className="impact-label">If unresolved</div>
                  <div className="impact-val" style={{ fontSize: 12 }}>
                    {root.expectedImpactIfUnresolved}
                  </div>
                </div>
                <div className="impact-box">
                  <div className="impact-label">Affected users</div>
                  <div className="impact-val" style={{ fontSize: 12 }}>
                    {root.affectedUsersEstimate}
                  </div>
                </div>
                <div className="impact-box">
                  <div className="impact-label">Model</div>
                  <div className="impact-val" style={{ fontSize: 12 }}>
                    {investigation.model}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      ) : null}
      <div className="ai-step">
        <div className="ai-step-head">
          <div className="ai-step-num">5</div>
          <div className="ai-step-title">Recommended remediation</div>
        </div>
        {investigation.remediations.map((action) => (
          <button
            key={action.id}
            type="button"
            className={`remed-option${selected?.id === action.id ? ' selected' : ''}`}
            onClick={() => onSelect(action.id)}
            disabled={executing || verified}
          >
            <div className="remed-option-head">
              <div className="remed-option-name">
                <div className="radio">
                  <div className="radio-dot" />
                </div>
                {action.title}
              </div>
              {action.recommended ? <span className="badge badge-ai">AI RECOMMENDED</span> : null}
            </div>
            <div className="remed-desc">{action.description}</div>
            <div className="remed-tags">
              <span className="badge badge-muted">risk: {action.risk}</span>
              <span className="badge badge-muted">~{action.etaMinutes} min</span>
            </div>
          </button>
        ))}
        <div className="approval-row">
          <div className="approval-info">
            {rejected ? 'Remediation rejected — incident remains open for manual handling.' : hint}
          </div>
          <div className="approval-btns">
            <button className="btn btn-ghost btn-sm" type="button" onClick={onReject} disabled={executing || verified}>
              Reject
            </button>
            <button
              className="btn btn-primary btn-sm"
              type="button"
              onClick={onApprove}
              disabled={!canApprove || executing || verified || rejected}
            >
              Approve & execute
            </button>
          </div>
        </div>
      </div>
      {execIndex >= 0 ? (
        <div className="ai-step">
          <div className="ai-step-head">
            <div className="ai-step-num">6</div>
            <div className="ai-step-title">Execution status</div>
          </div>
          <div className="exec-steps">
            {steps.map((step, index) => {
              const done = execIndex > index || verified;
              const active = execIndex === index && !verified;
              return (
                <div className={`exec-step${done ? ' done' : ''}${active ? ' active' : ''}`} key={step.name}>
                  <div className="exec-step-icon">
                    {done ? (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                        <path d="M5 12l5 5L20 7" />
                      </svg>
                    ) : (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <circle cx="12" cy="12" r="9" />
                      </svg>
                    )}
                  </div>
                  <div>
                    <div className="exec-step-name">{step.name}</div>
                    <div className="exec-step-detail">{step.detail}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
      {verified ? (
        <div className="ai-step">
          <div className="ai-step-head">
            <div className="ai-step-num">7</div>
            <div className="ai-step-title">Post-remediation verification</div>
          </div>
          <div className="verify-banner">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.3">
              <path d="M5 12l5 5L20 7" />
            </svg>
            <div>
              <div className="fw-700">Remediation verified successful</div>
              <div className="muted-sm">
                p95 latency returned to 240ms (baseline 250ms) · 5xx rate back to 0.1% · stable for 5 consecutive minutes
              </div>
            </div>
          </div>
          <div className="audit-note">Logged to audit trail — action_id: rem-8842</div>
        </div>
      ) : null}
    </>
  );
}

function rootCauseColor(confidence: number): string {
  if (confidence >= 85) return '#34D399';
  if (confidence >= 60) return '#F5A524';
  return '#F0465B';
}
