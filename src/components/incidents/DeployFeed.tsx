import type { Deployment } from '../../types';

interface DeployFeedProps {
  deployments: Deployment[];
}

export function DeployFeed({ deployments }: DeployFeedProps) {
  return (
    <>
      {deployments.map((deployment) => (
        <div className="gauge-row" key={deployment.id}>
          <div className="flex-center-9">
            <span className={`dot ${deployment.status === 'flagged' ? 'dot-warn' : 'dot-ok'}`} />
            <div>
              <div className="svc-name">
                {deployment.version} <span className="svc-sub">· {deployment.serviceName}</span>
              </div>
              <div className="inc-meta">
                {deployment.author} · {deployment.timeLabel} UTC
              </div>
            </div>
          </div>
          {deployment.status === 'flagged' ? (
            <span className="badge badge-sev2">FLAGGED</span>
          ) : (
            <span className="badge badge-ok">HEALTHY</span>
          )}
        </div>
      ))}
    </>
  );
}
