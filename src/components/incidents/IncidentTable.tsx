import type { Incident } from '../../types';
import { Badge, severityBadge, statusBadgeClass, statusLabel } from '../ui/Badge';

interface IncidentTableProps {
  incidents: Incident[];
  onOpen: (id: string) => void;
  title?: string;
  subtitle?: string;
}

export function IncidentTable({ incidents, onOpen, title = 'All Incidents', subtitle }: IncidentTableProps) {
  return (
    <div className="card">
      <div className="card-h">
        <div className="card-title">{title}</div>
        {subtitle ? <div className="card-sub">{subtitle}</div> : null}
      </div>
      <div className="inc-row head">
        <div className="th">ID</div>
        <div className="th">Title</div>
        <div className="th">Severity</div>
        <div className="th">Service</div>
        <div className="th">Status</div>
        <div className="th">Duration</div>
      </div>
      {incidents.length === 0 ? (
        <div className="empty-state">No incidents in this environment.</div>
      ) : (
        incidents.map((incident) => (
          <button key={incident.id} type="button" className="inc-row" onClick={() => onOpen(incident.id)}>
            <div className="inc-id">{incident.id}</div>
            <div className="inc-title">{incident.title}</div>
            <div>
              <Badge className={severityBadge(incident.severity)}>{incident.severity}</Badge>
            </div>
            <div className="inc-meta">{incident.serviceName}</div>
            <div>
              <Badge className={statusBadgeClass(incident.status)}>{statusLabel(incident.status)}</Badge>
            </div>
            <div className="inc-meta">{incident.durationLabel}</div>
          </button>
        ))
      )}
    </div>
  );
}
