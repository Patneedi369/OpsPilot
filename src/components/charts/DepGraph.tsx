import { topologyEdges, topologyNodes } from '../../data/services';
import type { ServiceHealth } from '../../types';

function colorOf(status: ServiceHealth): string {
  if (status === 'crit') return '#F0465B';
  if (status === 'warn') return '#F5A524';
  return '#34D399';
}

interface DepGraphProps {
  highlight?: boolean;
}

export function DepGraph({ highlight = true }: DepGraphProps) {
  const nodes = topologyNodes.map((node) => ({
    ...node,
    status: highlight ? node.status : ('ok' as const),
  }));
  const nodeMap = Object.fromEntries(nodes.map((node) => [node.id, node]));

  return (
    <svg className="dep-svg" viewBox="0 0 460 220" style={{ width: '100%', height: 240 }}>
      {topologyEdges.map((edge) => {
        const a = nodeMap[edge.from];
        const b = nodeMap[edge.to];
        const hi = highlight && edge.highlighted;
        return (
          <line
            key={`${edge.from}-${edge.to}`}
            x1={a.x}
            y1={a.y}
            x2={b.x}
            y2={b.y}
            stroke={hi ? '#F0465B' : '#2C3444'}
            strokeWidth={hi ? 2 : 1.2}
            strokeDasharray={hi ? '4,3' : undefined}
          />
        );
      })}
      {nodes.map((node) => (
        <g key={node.id}>
          <circle cx={node.x} cy={node.y} r="16" fill="#161B24" stroke={colorOf(node.status)} strokeWidth="1.8" />
          <circle cx={node.x} cy={node.y} r="4" fill={colorOf(node.status)} />
          <text x={node.x} y={node.y + 30} textAnchor="middle" className="dep-node-label">
            {node.label}
          </text>
        </g>
      ))}
    </svg>
  );
}
