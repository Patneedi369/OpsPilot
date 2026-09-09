import { useCallback, useEffect, useMemo, useState } from 'react';
import type { AppView, Incident, Investigation, UserRole } from './types';
import { incidents as seedIncidents } from './data/incidents';
import { fetchIncidents } from './services/api';
import { AppStateContext } from './hooks/useAppState';
import { Sidebar } from './components/layout/Sidebar';
import { Topbar } from './components/layout/Topbar';
import { OverviewPage } from './pages/OverviewPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { ServicesPage } from './pages/ServicesPage';
import { DeploymentsPage } from './pages/DeploymentsPage';
import { AuditLogPage } from './pages/AuditLogPage';
import { SettingsPage } from './pages/SettingsPage';
import { IncidentDetailPage } from './pages/IncidentDetailPage';

export default function App() {
  const [view, setView] = useState<AppView>('dashboard');
  const [role, setRole] = useState<UserRole>('sre');
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>(seedIncidents);
  const [investigations, setInvestigations] = useState<Record<string, Investigation>>({});
  const [auditNotes, setAuditNotes] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false;
    void fetchIncidents().then((list) => {
      if (!cancelled && list.length > 0) {
        setIncidents(list);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const openIncident = useCallback((id: string) => {
    setSelectedIncidentId(id);
    setView('incident-detail');
  }, []);

  const upsertIncident = useCallback((id: string, patch: Partial<Incident>) => {
    setIncidents((current) => current.map((item) => (item.id === id ? { ...item, ...patch } : item)));
  }, []);

  const setInvestigation = useCallback((incidentId: string, investigation: Investigation) => {
    setInvestigations((current) => ({ ...current, [incidentId]: investigation }));
  }, []);

  const appendAudit = useCallback((message: string) => {
    setAuditNotes((current) => [...current, message]);
  }, []);

  const state = useMemo(
    () => ({
      view,
      role,
      selectedIncidentId,
      incidents,
      investigations,
      auditNotes,
      setView,
      openIncident,
      setRole,
      upsertIncident,
      setInvestigation,
      appendAudit,
    }),
    [view, role, selectedIncidentId, incidents, investigations, auditNotes, openIncident, upsertIncident, setInvestigation, appendAudit],
  );

  return (
    <AppStateContext.Provider value={state}>
      <div className="shell">
        <Sidebar />
        <div className="main">
          <Topbar />
          <div className="content">
            {view === 'dashboard' ? <OverviewPage /> : null}
            {view === 'incidents' ? <IncidentsPage /> : null}
            {view === 'services' ? <ServicesPage /> : null}
            {view === 'deployments' ? <DeploymentsPage /> : null}
            {view === 'audit' ? <AuditLogPage /> : null}
            {view === 'settings' ? <SettingsPage /> : null}
            {view === 'incident-detail' ? <IncidentDetailPage /> : null}
          </div>
        </div>
      </div>
    </AppStateContext.Provider>
  );
}
