import type { Metric } from '../../types';

interface LineChartProps {
  metric: Metric;
  color?: string;
  max?: number;
  min?: number;
}

export function LineChart({ metric, color = '#4FC3F7', max, min = 0 }: LineChartProps) {
  const series = metric.series.map((point) => point.value);
  const labels = metric.series.map((point) => point.timestamp);
  const w = 900;
  const h = 180;
  const pad = { t: 14, r: 10, b: 22, l: 34 };
  const computedMax = max ?? Math.max(...series) * 1.15;
  const x = (i: number) => pad.l + (i / (series.length - 1)) * (w - pad.l - pad.r);
  const y = (v: number) => pad.t + (1 - (v - min) / (computedMax - min)) * (h - pad.t - pad.b);
  const path = series
    .map((v, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(v).toFixed(1)}`)
    .join(' ');
  const area = `${path} L${x(series.length - 1).toFixed(1)},${(h - pad.b).toFixed(1)} L${x(0).toFixed(1)},${(h - pad.b).toFixed(1)} Z`;
  const gradientId = `grad-${metric.id}`;
  const grid = [0, 1, 2, 3].map((i) => {
    const v = min + ((computedMax - min) * i) / 3;
    return (
      <g key={i}>
        <line x1={pad.l} y1={y(v)} x2={w - pad.r} y2={y(v)} stroke="#212836" strokeWidth="1" />
        <text x="4" y={y(v) + 3} className="dep-node-sub" fontSize="9">
          {Math.round(v)}
        </text>
      </g>
    );
  });
  const marker =
    metric.markerIndex !== undefined ? (
      <>
        <line
          x1={x(metric.markerIndex)}
          y1={pad.t}
          x2={x(metric.markerIndex)}
          y2={h - pad.b}
          stroke="#9B87F5"
          strokeWidth="1"
          strokeDasharray="3,3"
        />
        <text
          x={x(metric.markerIndex)}
          y={pad.t - 3}
          textAnchor="middle"
          fontSize="9"
          fill="#9B87F5"
          fontFamily="JetBrains Mono"
        >
          deploy
        </text>
      </>
    ) : null;

  return (
    <svg className="dep-svg" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" style={{ width: '100%', height: 180 }}>
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      {grid}
      {marker}
      <path d={area} fill={`${color}22`} />
      <path d={path} fill="none" stroke={color} strokeWidth="1.8" />
      {labels
        .filter((_, i) => i % 4 === 0)
        .map((label, idx) => (
          <text
            key={label}
            x={x(idx * 4)}
            y={h - 6}
            textAnchor="middle"
            fontSize="9"
            fill="#5A6578"
            fontFamily="JetBrains Mono"
          >
            {label}
          </text>
        ))}
    </svg>
  );
}
