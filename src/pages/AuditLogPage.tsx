import { auditEvents } from '../data/platform';
import { useAppState } from '../hooks/useAppState';

export function AuditLogPage() {
  const { auditNotes } = useAppState();
  const live = [...auditNotes].reverse();

  return (
    <div className="card">
      <div className="card-h">
        <div className="card-title">Audit Log</div>
        <div className="card-sub">Every AI recommendation, human decision & remediation action</div>
      </div>
      <div className="log-panel log-tall">
        {live.map((note, index) => (
          <div className="log-line" key={`live-${index}`}>
            <span className="log-time">[session]</span> {note}
          </div>
        ))}
        {auditEvents.map((event) => (
          <div className="log-line" key={event.id}>
            <span className="log-time">[{event.timestamp}]</span> {event.message}
          </div>
        ))}
      </div>
    </div>
  );
}
