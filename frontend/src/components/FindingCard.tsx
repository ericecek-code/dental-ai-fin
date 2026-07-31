/**
 * FindingCard – replaces DetectionCard.
 * Each finding: FDI tooth badge, condition name, confidence bar, severity.
 */

import { translateClass, translateSeverity } from '../lib/labels';

type Detection = {
  label: string;
  confidence: number;
  bbox: number[];
  severity: string;
  tooth_number?: string;
  class_id?: number;
};

type Props = {
  detections: Detection[];
  onHoverIndex?: (index: number | null) => void;
};

const SEVERITY_BORDER: Record<string, string> = {
  urgent: 'border-l-status-caries',
  treat_soon: 'border-l-status-lesion',
  watch: 'border-l-status-boneLoss',
};

const SEVERITY_DOT: Record<string, string> = {
  urgent: 'bg-status-caries',
  treat_soon: 'bg-status-lesion',
  watch: 'bg-status-boneLoss',
};

const CONFIDENCE_COLOR: Record<string, string> = {
  urgent: '#EF4444',
  treat_soon: '#F97316',
  watch: '#EAB308',
};

function confidenceColor(severity: string): string {
  return CONFIDENCE_COLOR[severity] || '#0D9488';
}

export default function FindingCard({ detections, onHoverIndex }: Props) {
  return (
    <div className="glass-panel p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
        Nájdené nálezy
      </h3>
      <div className="space-y-2 text-xs max-h-[320px] overflow-y-auto pr-1">
        {detections.length === 0 && (
          <p className="text-dental-textMuted text-center py-4">
            Žiadne nálezy
          </p>
        )}
        {detections.map((det, idx) => {
          const sk = translateClass(det.label);
          const severitySk = translateSeverity(det.severity);
          const tooth = det.tooth_number && det.tooth_number !== '?' ? det.tooth_number : null;
          const borderClass = SEVERITY_BORDER[det.severity] || 'border-l-dental-primary';

          return (
            <div
              key={idx}
              className={`
                rounded-lg border-l-4 ${borderClass}
                bg-slate-800/50 hover:bg-slate-700/50
                p-3 transition-all duration-200 cursor-default
                animate-fade-in
              `}
              style={{ animationDelay: `${idx * 50}ms` }}
              onMouseEnter={() => onHoverIndex?.(idx)}
              onMouseLeave={() => onHoverIndex?.(null)}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                {/* Tooth badge + class name */}
                <div className="flex items-center gap-2 min-w-0">
                  {tooth && (
                    <span className="shrink-0 px-2 py-0.5 rounded bg-dental-primary/20 text-dental-primary text-[10px] font-mono font-bold">
                      {tooth}
                    </span>
                  )}
                  <span className="font-medium text-dental-textMain truncate">
                    {sk}
                  </span>
                </div>

                {/* Severity badge */}
                <span className="shrink-0 flex items-center gap-1 text-[10px] text-dental-textMuted">
                  <span className={`w-1.5 h-1.5 rounded-full ${SEVERITY_DOT[det.severity] || 'bg-dental-primary'}`} />
                  {severitySk}
                </span>
              </div>

              {/* Confidence bar */}
              <div className="confidence-bar">
                <div
                  className="confidence-bar-fill"
                  style={{
                    width: `${det.confidence * 100}%`,
                    backgroundColor: confidenceColor(det.severity),
                  }}
                />
              </div>
              <div className="mt-1 flex justify-between text-[10px] text-dental-textMuted">
                <span>{sk !== det.label ? det.label : ''}</span>
                <span className="font-mono font-semibold" style={{ color: confidenceColor(det.severity) }}>
                  {(det.confidence * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
