import type { ReactNode } from 'react';
import type { IncidentEvent } from '../../types';

const icons: Record<IncidentEvent['type'], ReactNode> = {
  ok: (
    <svg viewBox="0 0 24 24" fill="none" stroke="#34D399" strokeWidth="3">
      <path d="M5 12l5 5L20 7" />
    </svg>
  ),
  warn: (
    <svg viewBox="0 0 24 24" fill="none" stroke="#F5A524" strokeWidth="3">
      <path d="M12 8v5M12 16h.01" />
    </svg>
  ),
  crit: (
    <svg viewBox="0 0 24 24" fill="none" stroke="#F0465B" strokeWidth="3">
      <path d="M12 8v5M12 16h.01" />
    </svg>
  ),
  deploy: (
    <svg viewBox="0 0 24 24" fill="none" stroke="#4FC3F7" strokeWidth="3">
      <rect x="4" y="4" width="16" height="16" rx="2" />
    </svg>
  ),
  ai: (
    <svg viewBox="0 0 24 24" fill="none" stroke="#9B87F5" strokeWidth="3">
      <path d="M12 2l2 6h6l-5 4 2 6-5-4-5 4 2-6-5-4h6z" />
    </svg>
  ),
};

interface TimelineProps {
  events: IncidentEvent[];
}

export function Timeline({ events }: TimelineProps) {
  if (events.length === 0) {
    return <div className="empty-state">No timeline events recorded.</div>;
  }

  return (
    <div className="tl">
      {events.map((event) => (
        <div className="tl-item" key={event.id}>
          <div className={`tl-dot ${event.type}`}>{icons[event.type]}</div>
          <div className="tl-time">{event.timestamp} UTC</div>
          <div className="tl-title">{event.title}</div>
          <div className="tl-desc">{event.description}</div>
        </div>
      ))}
    </div>
  );
}
