import type { ReactNode } from 'react';
import type { AppView } from '../../types';
import { useAppState } from '../../hooks/useAppState';

const items: Array<{ view: AppView; label: string; icon: ReactNode; badge?: boolean }> = [
  {
    view: 'dashboard',
    label: 'Overview',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
        <rect x="3" y="3" width="7" height="9" rx="1.5" />
        <rect x="14" y="3" width="7" height="5" rx="1.5" />
        <rect x="14" y="12" width="7" height="9" rx="1.5" />
        <rect x="3" y="16" width="7" height="5" rx="1.5" />
      </svg>
    ),
  },
  {
    view: 'incidents',
    label: 'Incidents',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
        <path d="M12 9v4M12 17h.01M10.3 3.9L2.5 17.5a1.8 1.8 0 001.5 2.7h16a1.8 1.8 0 001.5-2.7L13.7 3.9a1.8 1.8 0 00-3.4 0z" />
      </svg>
    ),
    badge: true,
  },
  {
    view: 'services',
    label: 'Services',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
        <circle cx="6" cy="6" r="3" />
        <circle cx="18" cy="6" r="3" />
        <circle cx="6" cy="18" r="3" />
        <circle cx="18" cy="18" r="3" />
        <path d="M9 6h6M6 9v6M18 9v6M9 18h6" />
      </svg>
    ),
  },
  {
    view: 'deployments',
    label: 'Deployments',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
        <rect x="3" y="4" width="18" height="16" rx="2" />
        <path d="M3 9h18M8 4v5" />
      </svg>
    ),
  },
];

export function Sidebar() {
  const { view, setView, incidents } = useAppState();
  const activeCount = incidents.filter((incident) => incident.status !== 'resolved').length;
  const navActive = view === 'incident-detail' ? 'incidents' : view;

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M12 2L3 7v10l9 5 9-5V7l-9-5z" stroke="#0A0D12" strokeWidth="1.6" strokeLinejoin="round" />
            <path d="M12 12l9-5M12 12v10M12 12L3 7" stroke="#0A0D12" strokeWidth="1.6" strokeLinejoin="round" />
          </svg>
        </div>
        <div>
          <div className="brand-name">OpsPilot</div>
          <div className="brand-sub">INCIDENT INTELLIGENCE</div>
        </div>
      </div>
      <nav className="nav">
        {items.map((item) => (
          <button
            key={item.view}
            type="button"
            className={`nav-item${navActive === item.view ? ' active' : ''}`}
            onClick={() => setView(item.view)}
          >
            {item.icon}
            <span>{item.label}</span>
            {item.badge ? <span className="nav-badge">{activeCount}</span> : null}
          </button>
        ))}
        <div className="nav-label">Platform</div>
        <button
          type="button"
          className={`nav-item${navActive === 'audit' ? ' active' : ''}`}
          onClick={() => setView('audit')}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
            <path d="M9 2h6l1 3h4v2H4V5h4l1-3z" />
            <path d="M6 7l1 13a2 2 0 002 2h6a2 2 0 002-2l1-13" />
          </svg>
          <span>Audit Log</span>
        </button>
        <button
          type="button"
          className={`nav-item${navActive === 'settings' ? ' active' : ''}`}
          onClick={() => setView('settings')}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.7 1.7 0 00.3 1.9l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.9-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 11-4 0v-.1a1.7 1.7 0 00-1-1.6 1.7 1.7 0 00-1.9.3l-.1.1a2 2 0 112.8-2.8l.1-.1a1.7 1.7 0 00.3-1.9 1.7 1.7 0 00-1.5-1H3a2 2 0 110-4h.1a1.7 1.7 0 001.6-1 1.7 1.7 0 00-.3-1.9l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.9.3H9a1.7 1.7 0 001-1.5V3a2 2 0 114 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.9-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.9V9a1.7 1.7 0 001.5 1H21a2 2 0 110 4h-.1a1.7 1.7 0 00-1.5 1z" />
          </svg>
          <span>Settings</span>
        </button>
      </nav>
      <div className="sidebar-foot">
        <div className="env-pill">
          <span className="env-dot" />
          <span>production · us-east-1</span>
        </div>
      </div>
    </aside>
  );
}
