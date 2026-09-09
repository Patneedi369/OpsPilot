import { platformSettings } from '../data/platform';

export function SettingsPage() {
  const s = platformSettings;
  return (
    <div className="card">
      <div className="card-h">
        <div className="card-title">Platform Settings</div>
      </div>
      <div className="gauge-row">
        <div className="gauge-label">Auto-approve remediations below risk threshold</div>
        <div className="badge badge-muted">{s.autoApproveBelowRisk ? 'ENABLED' : 'DISABLED'}</div>
      </div>
      <div className="gauge-row">
        <div className="gauge-label">Require dual approval for SEV-1 remediation</div>
        <div className="badge badge-ok">{s.dualApprovalSev1 ? 'ENABLED' : 'DISABLED'}</div>
      </div>
      <div className="gauge-row">
        <div className="gauge-label">AI investigation model</div>
        <div className="inc-meta">{s.investigationModel}</div>
      </div>
      <div className="gauge-row">
        <div className="gauge-label">RBAC roles</div>
        <div className="inc-meta">{s.rbacRoles}</div>
      </div>
    </div>
  );
}
