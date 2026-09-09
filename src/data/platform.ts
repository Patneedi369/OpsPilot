import type { AiInsight, AuditEvent, DashboardMetrics } from '../types';

export const dashboardMetrics: DashboardMetrics = {
  systemHealth: 82,
  healthDelta: 14,
  degradedServices: 1,
  activeIncidents: 3,
  sevBreakdown: { sev1: 1, sev2: 1, sev3: 1 },
  mttrMinutes: 18,
  mttrDeltaPct: 32,
  deploysToday: 7,
  deployServices: 6,
  flaggedDeploys: 1,
};

export const aiInsights: AiInsight[] = [
  {
    id: 'ins-1',
    text: 'Correlated deploy <b>#4821</b> on <b>order-service</b> with p95 latency increase beginning 21:04:12 UTC — investigation opened as INC-2043.',
    timeAgo: '2 min ago',
  },
  {
    id: 'ins-2',
    text: 'Redis eviction rate on <b>recs-cache</b> up 4.1x since 20:40 UTC. Likely undersized instance — no code change detected.',
    timeAgo: '18 min ago',
  },
  {
    id: 'ins-3',
    text: 'INC-2038 auto-verified resolved — token refresh p95 back within 180ms baseline for 15 consecutive minutes.',
    timeAgo: '1h ago',
  },
];

export const auditEvents: AuditEvent[] = [
  {
    id: 'aud-1',
    timestamp: '21:07:15',
    actor: 'opspilot-agent',
    message: 'opspilot-agent: evidence collection started for INC-2043',
    incidentId: 'INC-2043',
  },
  {
    id: 'aud-2',
    timestamp: '21:07:41',
    actor: 'opspilot-agent',
    message: 'opspilot-agent: correlated deploy #4821 with latency onset (Δ=43s)',
    incidentId: 'INC-2043',
  },
  {
    id: 'aud-3',
    timestamp: '21:08:02',
    actor: 'opspilot-agent',
    message: 'opspilot-agent: root-cause hypothesis generated, confidence=92%',
    incidentId: 'INC-2043',
  },
  {
    id: 'aud-4',
    timestamp: '21:08:03',
    actor: 'opspilot-agent',
    message: 'opspilot-agent: 2 remediation options proposed to on-call SRE',
    incidentId: 'INC-2043',
  },
  {
    id: 'aud-5',
    timestamp: '20:41:10',
    actor: 'opspilot-agent',
    message: 'opspilot-agent: INC-2041 opened — Redis eviction anomaly on recs-cache',
    incidentId: 'INC-2041',
  },
  {
    id: 'aud-6',
    timestamp: '19:02:55',
    actor: 'j.moreno@company.com',
    message: 'j.moreno@company.com: approved remediation "restart auth-token-cache" for INC-2038',
    incidentId: 'INC-2038',
  },
  {
    id: 'aud-7',
    timestamp: '19:03:20',
    actor: 'opspilot-agent',
    message: 'opspilot-agent: remediation executed — auth-token-cache restarted, 0 errors',
    incidentId: 'INC-2038',
  },
  {
    id: 'aud-8',
    timestamp: '19:12:40',
    actor: 'opspilot-agent',
    message: 'opspilot-agent: INC-2038 auto-verified resolved (15min stable window)',
    incidentId: 'INC-2038',
  },
];

export const platformSettings = {
  autoApproveBelowRisk: false,
  dualApprovalSev1: true,
  investigationModel: 'claude-sonnet-4-6',
  rbacRoles: 'SRE/DevOps · Platform Eng · Eng Manager',
};
