import { translateClass, translateSeverity } from '../lib/labels';

type Detection = {
  label: string;
  location: string;
  confidence: number;
  severity: string;
  description: string;
  bbox: number[] | null;
};

type Props = {
  detections: Detection[];
  rawText: string;
  assessment: string;
  isLoading: boolean;
  processingTimeMs: number;
};

const SEVERITY_COLORS: Record<string, string> = {
  urgent: 'border-red-400 bg-red-50',
  treat_soon: 'border-orange-400 bg-orange-50',
  watch: 'border-yellow-300 bg-yellow-50',
};

const SEVERITY_BADGE: Record<string, string> = {
  urgent: 'bg-red-500 text-white',
  treat_soon: 'bg-orange-500 text-white',
  watch: 'bg-yellow-400 text-black',
};

const GeminiPanel = ({ detections, rawText, assessment, isLoading, processingTimeMs }: Props) => {
  if (isLoading) {
    return (
      <div className="mt-4 rounded-lg border-2 border-purple-200 bg-purple-50 p-4">
        <div className="flex items-center gap-2">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-purple-500 border-t-transparent" />
          <span className="text-sm font-medium text-purple-700">Gemini analyzuje snímku...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-4 space-y-3">
      {/* Header */}
      <div className="rounded-lg border-2 border-purple-300 bg-gradient-to-r from-purple-50 to-indigo-50 p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-purple-800">🧠 Gemini Vision — Sudca</h3>
          <span className="text-xs text-purple-500">{processingTimeMs}ms</span>
        </div>
        {assessment && (
          <p className="mt-2 text-xs text-gray-700">{assessment}</p>
        )}
      </div>

      {/* Findings */}
      {detections.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-gray-600">Nájdené nálezy ({detections.length})</h4>
          {detections.map((det, i) => (
            <div
              key={i}
              className={`rounded-lg border p-3 ${SEVERITY_COLORS[det.severity] || 'border-gray-200 bg-white'}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold">{translateClass(det.label)}</span>
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${SEVERITY_BADGE[det.severity] || 'bg-gray-200'}`}>
                      {translateSeverity(det.severity)}
                    </span>
                  </div>
                  <div className="mt-1 text-xs text-gray-500">📍 {det.location}</div>
                  <div className="mt-1 text-xs text-gray-600">{det.description}</div>
                </div>
                <div className="shrink-0 text-right">
                  <div className="text-lg font-bold text-purple-700">{(det.confidence * 100).toFixed(0)}%</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Raw text (collapsible) */}
      <details className="rounded-lg border bg-white p-3">
        <summary className="cursor-pointer text-xs font-semibold text-gray-600">
          📄 Plný text odpovede Gemini
        </summary>
        <pre className="mt-2 max-h-96 overflow-auto whitespace-pre-wrap text-[11px] text-gray-600">
          {rawText}
        </pre>
      </details>
    </div>
  );
};

export default GeminiPanel;
