import type { Investigation } from '../types';
import { mockInvestigations } from '../data/investigations';
import { apiRequest } from './api';

export function investigateEndpoint(incidentId: string): string {
  return `/api/v1/incidents/${incidentId}/investigate`;
}

export interface InvestigationService {
  investigate(incidentId: string): Promise<Investigation>;
}

function isInvestigation(value: unknown): value is Investigation {
  if (!value || typeof value !== 'object') return false;
  const record = value as Record<string, unknown>;
  return (
    typeof record.id === 'string' &&
    typeof record.incidentId === 'string' &&
    Array.isArray(record.evidence) &&
    Array.isArray(record.remediations)
  );
}

function toInvestigation(payload: Investigation): Investigation {
  return {
    id: payload.id,
    incidentId: payload.incidentId,
    status: payload.status,
    evidence: payload.evidence,
    reasoning: payload.reasoning,
    rootCause: payload.rootCause,
    remediations: payload.remediations,
    model: payload.model,
  };
}

function offlineFallback(incidentId: string): Investigation {
  const cached = mockInvestigations[incidentId];
  if (cached) {
    return { ...cached, status: 'complete', incidentId };
  }
  return {
    id: `inv-${incidentId}`,
    incidentId,
    status: 'complete',
    model: 'offline-fallback',
    evidence: [
      {
        id: `${incidentId}-evd-1`,
        source: 'metrics',
        summary: `Backend unavailable; showing local fallback for ${incidentId}.`,
      },
    ],
    reasoning: 'The investigation API could not be reached, so OpsPilot used the local development fallback.',
    rootCause: {
      summary: `${incidentId} could not be investigated via the API.`,
      confidence: 0,
      expectedImpactIfUnresolved: 'Unknown while the backend is unreachable',
      affectedUsersEstimate: 'unknown',
      model: 'offline-fallback',
    },
    remediations: [
      {
        id: `${incidentId}-retry`,
        title: 'Retry investigation when API is available',
        description: 'Start the FastAPI backend and run the investigation again.',
        risk: 'low',
        etaMinutes: 1,
        recommended: true,
        kind: 'forward_fix',
      },
    ],
  };
}

export const investigationService: InvestigationService = {
  async investigate(incidentId: string): Promise<Investigation> {
    try {
      const payload = await apiRequest<Investigation>(investigateEndpoint(incidentId), { method: 'POST' });
      if (!isInvestigation(payload)) {
        throw new Error('Investigation response was missing required fields');
      }
      return toInvestigation(payload);
    } catch {
      return offlineFallback(incidentId);
    }
  },
};
