/**
 * SVG Odontogram – interactive FDI notation (11-48).
 * Shows upper + lower dental arches with colored teeth.
 */

type ToothStatus = 'healthy' | 'caries' | 'lesion' | 'implant' | 'bone_loss' | 'missing';

type ToothData = {
  fdi: string;
  status: ToothStatus;
  hasFinding?: boolean;
};

type Props = {
  findings?: Array<{ tooth_number?: string; label: string; severity: string }>;
};

const STATUS_COLORS: Record<ToothStatus, string> = {
  healthy: '#22C55E',
  caries: '#EF4444',
  lesion: '#F97316',
  implant: '#3B82F6',
  bone_loss: '#EAB308',
  missing: '#475569',
};

/** Map detection labels → odontogram status */
function deriveToothStatus(
  findings: NonNullable<Props['findings']>,
  fdi: string,
): ToothData['status'] {
  const toothFindings = findings.filter((f) => f.tooth_number === fdi);
  if (toothFindings.length === 0) return 'healthy';

  const labels = toothFindings.map((f) => f.label.toLowerCase());
  if (labels.some((l) => l.includes('implant'))) return 'implant';
  if (labels.some((l) => l.includes('caries') || l.includes('kaz'))) return 'caries';
  if (labels.some((l) => l.includes('lesion') || l.includes('lézia'))) return 'lesion';
  if (labels.some((l) => l.includes('bone') || l.includes('kos'))) return 'bone_loss';
  return 'healthy';
}

/** Generate all 32 FDI teeth */
function generateAllTeeth(findings: NonNullable<Props['findings']>): ToothData[] {
  const upperRight = ['18', '17', '16', '15', '14', '13', '12', '11'];
  const upperLeft = ['21', '22', '23', '24', '25', '26', '27', '28'];
  const lowerLeft = ['31', '32', '33', '34', '35', '36', '37', '38'];
  const lowerRight = ['41', '42', '43', '44', '45', '46', '47', '48'];

  const allFdi = [...upperRight, ...upperLeft, ...lowerLeft, ...lowerRight];
  const findingsWithTooth = findings.filter((f) => f.tooth_number);

  return allFdi.map((fdi) => {
    const hasFinding = findingsWithTooth.some((f) => f.tooth_number === fdi);
    return {
      fdi,
      status: deriveToothStatus(findings, fdi),
      hasFinding,
    };
  });
}

function Tooth({ tooth, x, y, w, h }: { tooth: ToothData; x: number; y: number; w: number; h: number }) {
  const color = STATUS_COLORS[tooth.status];
  const isMissing = tooth.status === 'missing';

  return (
    <g className={tooth.hasFinding ? 'tooth-pulse' : ''}>
      <rect
        x={x}
        y={y}
        width={w}
        height={h}
        rx={3}
        fill={isMissing ? 'none' : color}
        stroke={color}
        strokeWidth={isMissing ? 1.5 : 0.5}
        strokeDasharray={isMissing ? '3 2' : undefined}
        opacity={tooth.hasFinding ? 1 : 0.85}
      />
      <text
        x={x + w / 2}
        y={y + h / 2 + 1}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={8}
        fontWeight={600}
        fill={isMissing ? color : '#FFF'}
        style={{ userSelect: 'none' }}
      >
        {tooth.fdi}
      </text>
    </g>
  );
}

export default function Odontogram({ findings = [] }: Props) {
  const teeth = generateAllTeeth(findings);

  const svgWidth = 320;
  const toothW = 30;
  const toothH = 22;
  const gapX = 4;
  const gapY = 28;
  const startY = 10;

  // Upper arch: rows 0 (right) + 1 (left)
  const upperRight = teeth.filter((t) => t.fdi.startsWith('1'));
  const upperLeft = teeth.filter((t) => t.fdi.startsWith('2'));
  const lowerLeft = teeth.filter((t) => t.fdi.startsWith('3'));
  const lowerRight = teeth.filter((t) => t.fdi.startsWith('4'));

  return (
    <div className="glass-panel p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3 text-center">
        Odontogram
      </h3>
      <div className="flex justify-center overflow-x-auto">
        <svg
          width={svgWidth}
          height={2 * (toothH + gapY) + startY * 2 + 20}
          viewBox={`0 0 ${svgWidth} ${2 * (toothH + gapY) + startY * 2 + 20}`}
        >
          {/* Upper label */}
          <text x={svgWidth / 2} y={6} textAnchor="middle" fontSize={8} fill="#94A3B8" fontWeight={500}>
            Horný oblúk
          </text>

          {/* Upper right (18→11) */}
          {upperRight.map((t, i) => (
            <Tooth
              key={t.fdi}
              tooth={t}
              x={i * (toothW + gapX) + gapX}
              y={startY + 8}
              w={toothW}
              h={toothH}
            />
          ))}
          {/* Upper left (21→28) */}
          {upperLeft.map((t, i) => (
            <Tooth
              key={t.fdi}
              tooth={t}
              x={(8 + i) * (toothW + gapX) + gapX}
              y={startY + 8}
              w={toothW}
              h={toothH}
            />
          ))}

          {/* Separator line */}
          <line
            x1={10}
            y1={startY + 8 + toothH + 4}
            x2={svgWidth - 10}
            y2={startY + 8 + toothH + 4}
            stroke="rgba(148, 163, 184, 0.2)"
            strokeWidth={0.5}
          />

          {/* Lower left (31→38) */}
          {lowerLeft.map((t, i) => (
            <Tooth
              key={t.fdi}
              tooth={t}
              x={i * (toothW + gapX) + gapX}
              y={startY + 8 + toothH + gapY}
              w={toothW}
              h={toothH}
            />
          ))}
          {/* Lower right (41→48) */}
          {lowerRight.map((t, i) => (
            <Tooth
              key={t.fdi}
              tooth={t}
              x={(8 + i) * (toothW + gapX) + gapX}
              y={startY + 8 + toothH + gapY}
              w={toothW}
              h={toothH}
            />
          ))}

          {/* Lower label */}
          <text
            x={svgWidth / 2}
            y={startY + 8 + toothH + gapY + toothH + 14}
            textAnchor="middle"
            fontSize={8}
            fill="#94A3B8"
            fontWeight={500}
          >
            Dolný oblúk
          </text>
        </svg>
      </div>

      {/* Legend */}
      <div className="mt-3 flex flex-wrap justify-center gap-3 text-[10px] text-dental-textMuted">
        {Object.entries(STATUS_COLORS).filter(([k]) => k !== 'missing').map(([status, color]) => (
          <div key={status} className="flex items-center gap-1">
            <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: color }} />
            <span className="capitalize">
              {status === 'caries' ? 'Kaz' : status === 'lesion' ? 'Lézia' : status === 'implant' ? 'Implantát' : status === 'bone_loss' ? 'Úbytok kosti' : 'Zdravý'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
