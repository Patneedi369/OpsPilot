import { DepGraph } from '../components/charts/DepGraph';

export function ServicesPage() {
  return (
    <div className="card">
      <div className="card-h">
        <div className="card-title">Service Dependency Graph</div>
        <div className="card-sub">Full topology · production</div>
      </div>
      <DepGraph highlight />
    </div>
  );
}
