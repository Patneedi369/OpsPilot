import type { UserRole } from '../../types';
import { useAppState, viewTitles } from '../../hooks/useAppState';

export function Topbar() {
  const { view, selectedIncidentId, role, setRole } = useAppState();
  const title = view === 'incident-detail' && selectedIncidentId ? selectedIncidentId : viewTitles[view];

  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className="crumb">
          <b>{title}</b>
        </div>
      </div>
      <div className="topbar-right">
        <select
          className="role-select"
          value={role}
          onChange={(event) => setRole(event.target.value as UserRole)}
        >
          <option value="sre">Role: SRE / DevOps</option>
          <option value="platform">Role: Platform Eng</option>
          <option value="em">Role: Eng Manager</option>
        </select>
        <button className="icon-btn" type="button" title="Notifications">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
            <path d="M18 8a6 6 0 10-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.7 21a2 2 0 01-3.4 0" />
          </svg>
        </button>
        <div className="avatar">SK</div>
      </div>
    </div>
  );
}
