import type { Investigation } from '../types';
import { mockInvestigations } from '../data/investigations';

export function investigateEndpoint(incidentId: string): string {
  return `/api/v1/incidents/${incidentId}/investigate`;
}

export interface InvestigationService {
  investigate(incidentId: string): Promise<Investigation>;
}

async function mockDelay(ms = 1400): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

function fallbackInvestigation(incidentId: string): Investigation {
  return {
    id: `inv-${incidentId}`,
    incidentId,
    status: 'complete',
    model: 'claude-sonnet-4-6',
    evidence: [
      {
        id: `${incidentId}-evd-1`,
        source: 'metrics',
        summary: `Telemetry for ${incidentId} is available, but no new cascading failure pattern is present.`,
      },
    ],
    reasoning:
      'The available signals are consistent with a contained or already-mitigated issue. No unindexed query, pool exhaustion, or correlated deploy is in the current evidence set.',
    rootCause: {
      summary: `${incidentId} does not currently exhibit an active cascading production failure.`,
      confidence: 70,
      expectedImpactIfUnresolved: 'Limited residual user impact',
      affectedUsersEstimate: 'contained',
      model: 'claude-sonnet-4-6',
    },
    remediations: [
      {
        id: `${incidentId}-watch`,
        title: 'Continue monitoring',
        description: 'Keep SLO burn alerts armed and close if the window remains stable.',
        risk: 'low',
        etaMinutes: 5,
        recommended: true,
        kind: 'forward_fix',
      },
    ],
  };
}

export const investigationService: InvestigationService = {
  async investigate(incidentId: string): Promise<Investigation> {
    // Later this becomes: POST investigateEndpoint(incidentId)
    await mockDelay();
    const result = mockInvestigations[incidentId] ?? fallbackInvestigation(incidentId);
    return { ...result, status: 'complete', incidentId };
  },
};
