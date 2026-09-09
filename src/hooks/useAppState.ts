import type {
  AppView,
  Incident,
  IncidentSection,
  Investigation,
  UserRole,
  WorkflowStage,
} from '../types';
import { createContext, useContext } from 'react';

export const viewTitles: Record<AppView, string> = {
  dashboard: 'Overview',
  incidents: 'Incidents',
  services: 'Services',
  deployments: 'Deployments',
  audit: 'Audit Log',
  settings: 'Settings',
  'incident-detail': 'Incident',
};

export const workflowStages: Array<{ id: WorkflowStage; label: string }> = [
  { id: 'detection', label: 'Detection' },
  { id: 'investigation', label: 'Investigation' },
  { id: 'evidence', label: 'Evidence' },
  { id: 'correlation', label: 'Correlation' },
  { id: 'root_cause', label: 'Root cause' },
  { id: 'remediation_proposal', label: 'Remediation' },
  { id: 'human_approval', label: 'Approval' },
  { id: 'execution', label: 'Execution' },
  { id: 'verification', label: 'Verification' },
  { id: 'resolution', label: 'Resolution' },
];

export const incidentSections: Array<{ id: IncidentSection; label: string }> = [
  { id: 'sum', label: 'Summary' },
  { id: 'metrics', label: 'Metrics' },
  { id: 'logs', label: 'Logs' },
  { id: 'deploy', label: 'Deployments' },
  { id: 'db', label: 'Database' },
  { id: 'dep', label: 'Dependencies' },
  { id: 'ai', label: 'AI Investigation' },
];

export interface AppState {
  view: AppView;
  role: UserRole;
  selectedIncidentId: string | null;
  incidents: Incident[];
  investigations: Record<string, Investigation>;
  auditNotes: string[];
  setView: (view: AppView) => void;
  openIncident: (id: string) => void;
  setRole: (role: UserRole) => void;
  upsertIncident: (id: string, patch: Partial<Incident>) => void;
  setInvestigation: (incidentId: string, investigation: Investigation) => void;
  appendAudit: (message: string) => void;
}

export const AppStateContext = createContext<AppState | null>(null);

export function useAppState(): AppState {
  const ctx = useContext(AppStateContext);
  if (!ctx) throw new Error('useAppState must be used within App');
  return ctx;
}
