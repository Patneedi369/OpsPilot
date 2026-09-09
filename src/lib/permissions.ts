import type { RemediationAction, UserRole } from '../types';

export function roleLabel(role: UserRole): string {
  if (role === 'sre') return 'SRE/DevOps';
  if (role === 'platform') return 'Platform Eng';
  return 'Eng Manager';
}

export function canRunInvestigation(role: UserRole): boolean {
  return role === 'sre' || role === 'platform';
}

export function canApproveRemediation(role: UserRole, action: RemediationAction): boolean {
  if (role === 'em') return false;
  if (role === 'sre') return true;
  return action.kind === 'infrastructure' || action.kind === 'forward_fix';
}

export function approvalHint(role: UserRole, action?: RemediationAction): string {
  if (role === 'em') {
    return 'Viewing as Eng Manager — approval restricted to SRE/DevOps or Platform Eng.';
  }
  if (role === 'platform' && action?.kind === 'rollback') {
    return 'Platform Eng can manage infrastructure actions; rollback approval is reserved for SRE/DevOps.';
  }
  return `Approving as ${roleLabel(role)} — action will be logged to the audit trail.`;
}
