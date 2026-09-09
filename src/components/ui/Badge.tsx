import type { IncidentSeverity, IncidentStatus } from '../../types';

export function severityBadge(severity: IncidentSeverity): string {
  if (severity === 'SEV-1') return 'badge badge-sev1';
  if (severity === 'SEV-2') return 'badge badge-sev2';
  return 'badge badge-sev3';
}

export function statusBadgeClass(status: IncidentStatus): string {
  if (status === 'resolved') return 'badge badge-ok';
  if (status === 'investigating' || status === 'executing' || status === 'verifying') {
    return 'badge badge-ai';
  }
  return 'badge badge-muted';
}

export function statusLabel(status: IncidentStatus): string {
  const labels: Record<IncidentStatus, string> = {
    detected: 'DETECTED',
    investigating: 'AI INVESTIGATING',
    awaiting_approval: 'AWAITING APPROVAL',
    executing: 'EXECUTING',
    verifying: 'VERIFYING',
    monitoring: 'MONITORING',
    resolved: 'RESOLVED',
  };
  return labels[status];
}

interface BadgeProps {
  className: string;
  children: string;
}

export function Badge({ className, children }: BadgeProps) {
  return <span className={className}>{children}</span>;
}
