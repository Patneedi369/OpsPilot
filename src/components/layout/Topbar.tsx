import { useState } from 'react';
import type { UserRole } from '../../types';
import { useAppState, viewTitles } from '../../hooks/useAppState';

export function Topbar() {
  const { view, selectedIncidentId, role, setRole, incidents, openIncident } = useAppState();
  const [showNotifications, setShowNotifications] = useState(false);
  const [readIds, setReadIds] = useState<string[]>([]);

  // Dynamically derive notification items from real incident data in app state
  const activeIncidents = incidents.filter((item) => item.status !== 'resolved');
  const notifications = activeIncidents.map((inc) => ({
    id: inc.id,
    title: `${inc.severity} Incident Active`,
    message: `${inc.id} — ${inc.title} (${inc.serviceName})`,
    time: inc.startedAt ?? 'Recently',
    unread: !readIds.includes(inc.id),
    incidentId: inc.id,
    type: inc.severity === 'SEV-1' ? 'crit' : 'warn',
  }));

  const unreadCount = notifications.filter((n) => n.unread).length;
  const title = view === 'incident-detail' && selectedIncidentId ? selectedIncidentId : viewTitles[view];

  const handleMarkAllRead = () => {
    setReadIds(notifications.map((n) => n.id));
  };

  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className="crumb">
          <b>{title}</b>
        </div>
      </div>
      <div className="topbar-right" style={{ position: 'relative' }}>
        <select
          className="role-select"
          value={role}
          onChange={(event) => setRole(event.target.value as UserRole)}
        >
          <option value="sre">Role: SRE / DevOps</option>
          <option value="platform">Role: Platform Eng</option>
          <option value="em">Role: Eng Manager</option>
        </select>

        <div style={{ position: 'relative' }}>
          <button
            className="icon-btn"
            type="button"
            title="Notifications"
            onClick={() => setShowNotifications(!showNotifications)}
            style={{ position: 'relative' }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M18 8a6 6 0 10-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.7 21a2 2 0 01-3.4 0" />
            </svg>
            {unreadCount > 0 && (
              <span
                style={{
                  position: 'absolute',
                  top: '-2px',
                  right: '-2px',
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: 'var(--sev-1)',
                  boxShadow: '0 0 6px var(--sev-1)',
                }}
              />
            )}
          </button>

          {showNotifications && (
            <div className="notif-dropdown">
              <div className="notif-header">
                <div className="notif-title">Notifications</div>
                {unreadCount > 0 ? (
                  <button type="button" className="notif-mark-read" onClick={handleMarkAllRead}>
                    Mark all read
                  </button>
                ) : (
                  <span className="notif-status-clean">All caught up</span>
                )}
              </div>

              <div className="notif-list">
                {notifications.length === 0 || unreadCount === 0 ? (
                  <div className="notif-empty">
                    <div style={{ fontWeight: 600, color: 'var(--text-1)', marginBottom: '4px' }}>
                      No unread notifications
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-3)' }}>
                      System alerts and active incident updates will appear here.
                    </div>
                  </div>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className={`notif-item ${n.unread ? 'unread' : ''}`}
                      onClick={() => {
                        if (n.incidentId) {
                          openIncident(n.incidentId);
                          setShowNotifications(false);
                        }
                      }}
                    >
                      <div className="notif-item-top">
                        <span className={`notif-badge notif-badge-${n.type}`}>
                          {n.type === 'crit' ? 'SEV-1' : 'WARN'}
                        </span>
                        <span className="notif-time">{n.time}</span>
                      </div>
                      <div className="notif-item-title">{n.title}</div>
                      <div className="notif-item-msg">{n.message}</div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="avatar">SK</div>
      </div>
    </div>
  );
}

