import { useMemo } from 'react';

type Props = {
  /** 0–100 overall dental health score */
  score: number;
  /** Optional label below the score */
  label?: string;
};

const HEALTH_COLOR_STOPS = [
  { threshold: 30, color: '#EF4444' },   // red
  { threshold: 60, color: '#F97316' },   // orange
  { threshold: 80, color: '#EAB308' },   // yellow
  { threshold: 100, color: '#22C55E' },  // green
];

function getColor(score: number): string {
  for (const stop of HEALTH_COLOR_STOPS) {
    if (score <= stop.threshold) return stop.color;
  }
  return '#22C55E';
}

function getLabel(score: number): string {
  if (score <= 30) return 'Kritický stav';
  if (score <= 60) return 'Potrebná liečba';
  if (score <= 80) return 'Dobrý stav';
  return 'Výborný stav';
}

export default function HealthScoreGauge({ score, label }: Props) {
  const clampedScore = Math.max(0, Math.min(100, score));
  const color = useMemo(() => getColor(clampedScore), [clampedScore]);

  // SVG circle geometry
  const size = 180;
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (clampedScore / 100) * circumference;
  const center = size / 2;

  // Gradient id
  const gradientId = 'gauge-gradient';

  return (
    <div className="glass-panel p-5 flex flex-col items-center">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
        Zdravotný skóre
      </h3>

      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <defs>
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0D9488" />
              <stop offset="100%" stopColor="#06B6D4" />
            </linearGradient>
          </defs>

          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="rgba(51, 65, 85, 0.4)"
            strokeWidth={strokeWidth}
          />

          {/* Progress arc */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={`url(#${gradientId})`}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
            style={{
              transition: 'stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1)',
              filter: `drop-shadow(0 0 6px ${color}40)`,
            }}
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-3xl font-bold"
            style={{ color, textShadow: `0 0 20px ${color}50` }}
          >
            {clampedScore}
          </span>
          <span className="text-[10px] font-medium text-dental-textMuted uppercase tracking-wider">
            %
          </span>
        </div>
      </div>

      <p className="mt-3 text-xs font-medium text-dental-textMuted">
        {label || getLabel(clampedScore)}
      </p>
    </div>
  );
}
