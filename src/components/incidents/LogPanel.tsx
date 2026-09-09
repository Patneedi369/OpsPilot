import type { LogEntry } from '../../types';
import { padLogLevel } from '../../lib/format';

interface LogPanelProps {
  entries: LogEntry[];
  maxHeight?: number;
}

export function LogPanel({ entries, maxHeight }: LogPanelProps) {
  if (entries.length === 0) {
    return <div className="log-panel empty-state">No log entries for this window.</div>;
  }

  return (
    <div className="log-panel" style={maxHeight ? { maxHeight } : undefined}>
      {entries.map((entry) => (
        <div className="log-line" key={entry.id}>
          <span className="log-time">{entry.timestamp}</span>{' '}
          <span className={`log-lvl-${entry.level}`}>{padLogLevel(entry.level)}</span>{' '}
          <span className="log-svc">[{entry.service}]</span> {entry.message}
        </div>
      ))}
    </div>
  );
}
