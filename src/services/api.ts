import type { Incident } from '../types';
import { getIncident, incidents as mockIncidents } from '../data/incidents';

export function apiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_BASE_URL;
  return configured?.replace(/\/$/, '') ?? '';
}

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${apiBaseUrl()}${path}`;
  try {
    const response = await fetch(url, {
      ...init,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...init?.headers,
      },
    });
    if (!response.ok) {
      console.warn(`[OpsPilot API] HTTP ${response.status} ${response.statusText} for ${path}`);
      throw new ApiError(response.status, `${response.status} ${response.statusText} for ${path}`);
    }
    return response.json() as Promise<T>;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    console.warn(`[OpsPilot API Network Alert] Failed to reach ${url}:`, err);
    throw err;
  }
}

export interface HealthResponse {
  status: string;
  service: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>('/api/v1/health');
}

export async function fetchIncidents(): Promise<Incident[]> {
  try {
    const incidents = await apiRequest<Incident[]>('/api/v1/incidents');
    if (!Array.isArray(incidents) || incidents.length === 0) {
      return mockIncidents;
    }
    return incidents;
  } catch (err) {
    console.info('[OpsPilot API] Using resilience fallback for incident list:', err);
    return mockIncidents;
  }
}

export async function fetchIncidentById(incidentId: string): Promise<Incident | undefined> {
  try {
    return await apiRequest<Incident>(`/api/v1/incidents/${incidentId}`);
  } catch (err) {
    console.info(`[OpsPilot API] Using resilience fallback for incident ${incidentId}:`, err);
    return getIncident(incidentId);
  }
}

export interface AuditLogRecord {
  id: string;
  user_id: string;
  username: string;
  user_role: string;
  action: string;
  resource_type: string;
  resource_id: string;
  outcome: string;
  metadata_json?: Record<string, unknown>;
  created_at: string;
}

export async function fetchAuditLogs(roleHeader = 'Lead'): Promise<AuditLogRecord[]> {
  try {
    return await apiRequest<AuditLogRecord[]>('/api/v1/audit/logs', {
      headers: { 'X-User-Role': roleHeader },
    });
  } catch (err) {
    console.info('[OpsPilot API] Using empty log array for audit logs fallback:', err);
    return [];
  }
}

