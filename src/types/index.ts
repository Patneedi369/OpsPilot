export type UserRole = 'sre' | 'platform' | 'em';

export type IncidentSeverity = 'SEV-1' | 'SEV-2' | 'SEV-3';

export type IncidentStatus =
  | 'detected'
  | 'investigating'
  | 'awaiting_approval'
  | 'executing'
  | 'verifying'
  | 'monitoring'
  | 'resolved';

export type WorkflowStage =
  | 'detection'
  | 'investigation'
  | 'evidence'
  | 'correlation'
  | 'root_cause'
  | 'remediation_proposal'
  | 'human_approval'
  | 'execution'
  | 'verification'
  | 'resolution';

export type IncidentEventType = 'deploy' | 'warn' | 'crit' | 'ai' | 'ok';

export interface IncidentEvent {
  id: string;
  incidentId: string;
  timestamp: string;
  title: string;
  description: string;
  type: IncidentEventType;
}

export type ServiceHealth = 'ok' | 'warn' | 'crit';

export interface Service {
  id: string;
  name: string;
  kind: 'service' | 'datastore' | 'gateway' | 'cache';
  health: ServiceHealth;
  p95LatencyMs?: number;
  note?: string;
}

export interface ServiceEdge {
  from: string;
  to: string;
  highlighted: boolean;
}

export interface Deployment {
  id: string;
  version: string;
  serviceId: string;
  serviceName: string;
  author: string;
  authorEmail: string;
  deployedAt: string;
  timeLabel: string;
  status: 'healthy' | 'flagged';
  commit: string;
  commitMessage: string;
  filesChanged: string;
  diffExcerpt?: string[];
}

export type LogLevel = 'INFO' | 'WARN' | 'ERROR';

export interface LogEntry {
  id: string;
  timestamp: string;
  level: LogLevel;
  service: string;
  message: string;
}

export interface MetricPoint {
  timestamp: string;
  value: number;
}

export interface Metric {
  id: string;
  name: string;
  unit: string;
  series: MetricPoint[];
  markerIndex?: number;
}

export type EvidenceSource = 'metrics' | 'logs' | 'deployment' | 'database' | 'topology';

export interface Evidence {
  id: string;
  source: EvidenceSource;
  summary: string;
}

export type RemediationRisk = 'low' | 'medium' | 'high';

export interface RemediationAction {
  id: string;
  title: string;
  description: string;
  risk: RemediationRisk;
  etaMinutes: number;
  recommended: boolean;
  kind: 'rollback' | 'infrastructure' | 'forward_fix';
}

export interface RootCause {
  summary: string;
  confidence: number;
  expectedImpactIfUnresolved: string;
  affectedUsersEstimate: string;
  model: string;
}

export type InvestigationRunStatus =
  | 'running'
  | 'awaiting_approval'
  | 'approved'
  | 'rejected'
  | 'executing'
  | 'verifying_recovery'
  | 'recovered'
  | 'remediation_failed'
  | 'verification_failed'
  | 'completed'
  | 'failed';

export interface RemediationExecutionDetail {
  startedAt: string;
  completedAt: string;
  status: 'succeeded' | 'failed';
  actionsPerformed: Array<{ action: string; status: string; durationMs?: string }>;
  details: string;
  error?: string;
}

export interface RecoveryVerificationDetail {
  verifiedAt: string;
  status: 'recovered' | 'verification_failed';
  signalsChecked: Array<{ metric: string; observed: number; threshold: number; unit: string; status: 'PASS' | 'FAIL' }>;
  details: string;
  error?: string;
}

export interface InvestigationRun {
  id: string;
  incidentId: string;
  threadId: string;
  status: InvestigationRunStatus;
  currentStep: string;
  startedAt: string;
  completedAt?: string;
  finalResult?: Record<string, unknown>;
  errorMessage?: string;
  approvalDecision?: 'approved' | 'rejected';
  approvalActor?: string;
  approvalNote?: string;
  approvedAt?: string;
  executionResult?: RemediationExecutionDetail;
  verificationResult?: RecoveryVerificationDetail;
}

export interface Investigation {
  id: string;
  incidentId: string;
  status: 'idle' | 'running' | 'complete' | 'failed' | InvestigationRunStatus;
  evidence: Evidence[];
  reasoning: string;
  rootCause: RootCause | null;
  remediations: RemediationAction[];
  model: string;
  observedEvidence?: string[];
  inferredRelationship?: string;
  alternativeHypotheses?: string[];
  assumptions?: string[];
  missingEvidence?: string[];
  providerMetadata?: Record<string, unknown>;
}

export type ApprovalDecision = 'pending' | 'approved' | 'rejected';

export interface Approval {
  id: string;
  incidentId: string;
  remediationId: string;
  decision: ApprovalDecision;
  requestedRole: UserRole;
  decidedByRole?: UserRole;
  decidedAt?: string;
  note?: string;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  actor: string;
  message: string;
  incidentId?: string;
}

export interface Incident {
  id: string;
  title: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  workflowStage: WorkflowStage;
  serviceId: string;
  serviceName: string;
  startedAt: string;
  durationLabel: string;
  elapsedSeconds: number;
  trigger: string;
  affectedServices: Array<{
    serviceId: string;
    name: string;
    health: ServiceHealth;
    metric: string;
  }>;
  blastRadius: string;
}

export interface DashboardMetrics {
  systemHealth: number;
  healthDelta: number;
  degradedServices: number;
  activeIncidents: number;
  sevBreakdown: { sev1: number; sev2: number; sev3: number };
  mttrMinutes: number;
  mttrDeltaPct: number;
  deploysToday: number;
  deployServices: number;
  flaggedDeploys: number;
}

export interface AiInsight {
  id: string;
  text: string;
  timeAgo: string;
}

export interface DatabaseHealth {
  connectionPoolUtilPct: number;
  avgQueryTimeMs: number;
  activeConnections: number;
  maxConnections: number;
  replicationLagSec: number;
  deadlocksPerMin: number;
}

export interface DatabaseEvidence {
  poolInUse: number;
  poolMax: number;
  avgQueryTimeMs: number;
  rowsScanned: string;
  queuedConnections: number;
  slowQueries: Array<{ durationMs: number; sql: string }>;
}

export type AppView =
  | 'dashboard'
  | 'incidents'
  | 'services'
  | 'deployments'
  | 'audit'
  | 'settings'
  | 'incident-detail';

export type IncidentSection =
  | 'sum'
  | 'metrics'
  | 'logs'
  | 'deploy'
  | 'db'
  | 'dep'
  | 'ai';
