import { deployments } from '../data/deployments';
import { DeployFeed } from '../components/incidents/DeployFeed';

export function DeploymentsPage() {
  return (
    <div className="card">
      <div className="card-h">
        <div className="card-title">Deployment History</div>
      </div>
      <DeployFeed deployments={deployments} />
    </div>
  );
}
