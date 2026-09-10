import { useEffect, useState } from 'react';
import { auditEvents } from '../data/platform';
import { useAppState } from '../hooks/useAppState';
import { fetchAuditLogs, type AuditLogRecord } from '../services/api';

export function AuditLogPage() {
  const { role, auditNotes } = useAppState();
  const [backendLogs, setBackendLogs] = useState<AuditLogRecord[]>([]);
  const live = [...auditNotes].reverse();

  useEffect(() => {
    fetchAuditLogs(role).then(setBackendLogs).catch(() => setBackendLogs([]));
  }, [role]);

  return (
    <div className="card">
      <div className="card-h">
        <div className="card-title">Audit Log</div>
        <div className="card-sub">Every AI recommendation, human decision & remediation action</div>
      </div>
      <div className="log-panel log-tall">
        {backendLogs.length > 0
          ? backendLogs.map((log) => (
              <div className="log-line" key={log.id}>
                <span className="log-time">[{new Date(log.created_at).toLocaleTimeString()}]</span>{' '}
                <strong style={{ color: '#60A5FA' }}>[{log.username} ({log.user_role})]</strong>{' '}
                <span style={{ color: log.outcome === 'success' ? '#34D399' : '#F0465B' }}>[{log.action}]</span>{' '}
                {log.resource_type}:{log.resource_id}
              </div>
            ))
          : null}
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
