import { IncidentTable } from '../components/incidents/IncidentTable';
import { useAppState } from '../hooks/useAppState';

export function IncidentsPage() {
  const { incidents, openIncident } = useAppState();
  return <IncidentTable incidents={incidents} onOpen={openIncident} />;
}
