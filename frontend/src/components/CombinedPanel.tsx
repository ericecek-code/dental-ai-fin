import { translateClass, translateSeverity } from '../lib/labels';

type MatchedFinding = {
  label: string;
  label_sk: string;
  tooth: string;
  yolo_confidence: number;
  gemini_confidence: number;
  severity: string;
  description_yolo: string;
  description_gemini: string;
};

type SingleFinding = {
  label: string;
  tooth: string;
  confidence: number;
  severity: string;
  description?: string;
};

type ComparisonResult = {
  matched: MatchedFinding[];
  yolo_only: SingleFinding[];
  gemini_only: SingleFinding[];
  summary: {
    yolo_count: number;
    gemini_count: number;
    matched_count: number;
    yolo_only_count: number;
    gemini_only_count: number;
  };
};

type GeminiDetection = {
  label: string;
  tooth?: string;
  quadrant?: number;
  location: string;
  confidence: number;
  severity: string;
  description: string;
  bbox: number[] | null;
};

type Props = {
  comparison: ComparisonResult;
  geminiAssessment?: string;
  totalTimeMs: number;
};

const SEVERITY_BADGE: Record<string, string> = {
  urgent: 'bg-red-500 text-white',
  treat_soon: 'bg-orange-500 text-white',
  watch: 'bg-yellow-400 text-black',
};

const CombinedPanel = ({ comparison, geminiAssessment, totalTimeMs }: Props) => {
  const s = comparison.summary;

  return (
    <div className="mt-4 space-y-3">
      {/* Summary */}
      <div className="rounded-lg border-2 border-indigo-300 bg-gradient-to-r from-indigo-50 to-purple-50 p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-indigo-800">⚖️ Porovnanie YOLO vs Gemini</h3>
          <span className="text-xs text-indigo-500">Celkom: {totalTimeMs}ms</span>
        </div>
        <div className="mt-2 grid grid-cols-4 gap-2 text-center text-xs">
          <div className="rounded bg-blue-100 p-2">
            <div className="text-lg font-bold text-blue-700">{s.yolo_count}</div>
            <div className="text-blue-600">YOLO</div>
          </div>
          <div className="rounded bg-purple-100 p-2">
            <div className="text-lg font-bold text-purple-700">{s.gemini_count}</div>
            <div className="text-purple-600">Gemini</div>
          </div>
          <div className="rounded bg-green-100 p-2">
            <div className="text-lg font-bold text-green-700">{s.matched_count}</div>
            <div className="text-green-600">Zhodné</div>
          </div>
          <div className="rounded bg-orange-100 p-2">
            <div className="text-lg font-bold text-orange-700">{s.yolo_only_count + s.gemini_only_count}</div>
            <div className="text-orange-600">Rozdiely</div>
          </div>
        </div>
      </div>

      {/* MATCHED — table side by side */}
      {comparison.matched.length > 0 && (
        <div className="rounded-lg border bg-white p-3">
          <h4 className="mb-2 text-xs font-bold text-green-700">✅ Zhodné nálezy ({s.matched_count})</h4>
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="py-1 pr-2">Nález</th>
                <th className="py-1 pr-2">Zub</th>
                <th className="py-1 pr-2 text-center">YOLO</th>
                <th className="py-1 pr-2 text-center">Gemini</th>
                <th className="py-1 text-center">Stav</th>
              </tr>
            </thead>
            <tbody>
              {comparison.matched.map((m, i) => (
                <tr key={i} className="border-b last:border-0">
                  <td className="py-1.5 pr-2 font-semibold">{translateClass(m.label)}</td>
                  <td className="py-1.5 pr-2 text-gray-600">{m.tooth || '—'}</td>
                  <td className="py-1.5 pr-2 text-center text-blue-600">{(m.yolo_confidence * 100).toFixed(0)}%</td>
                  <td className="py-1.5 pr-2 text-center text-purple-600">{(m.gemini_confidence * 100).toFixed(0)}%</td>
                  <td className="py-1.5 text-center">
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${SEVERITY_BADGE[m.severity] || 'bg-gray-200'}`}>
                      {translateSeverity(m.severity)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* YOLO only */}
      {comparison.yolo_only.length > 0 && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-3">
          <h4 className="mb-2 text-xs font-bold text-blue-700">🔍 Iba YOLO ({s.yolo_only_count})</h4>
          {comparison.yolo_only.map((d, i) => (
            <div key={i} className="mb-1 flex items-center justify-between rounded bg-white px-2 py-1 text-xs">
              <span>{translateClass(d.label)} {d.tooth ? `(${d.tooth})` : ''}</span>
              <span className="text-gray-500">{(d.confidence * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      )}

      {/* Gemini only */}
      {comparison.gemini_only.length > 0 && (
        <div className="rounded-lg border border-purple-200 bg-purple-50 p-3">
          <h4 className="mb-2 text-xs font-bold text-purple-700">🧠 Iba Gemini ({s.gemini_only_count})</h4>
          {comparison.gemini_only.map((d, i) => (
            <div key={i} className="mb-1 rounded bg-white px-2 py-1 text-xs">
              <div className="flex items-center justify-between">
                <span>{translateClass(d.label)} {d.tooth ? `(${d.tooth})` : ''}</span>
                <span className="text-gray-500">{(d.confidence * 100).toFixed(0)}%</span>
              </div>
              {d.description && <div className="text-gray-400 italic">{d.description}</div>}
            </div>
          ))}
        </div>
      )}

      {/* Gemini assessment */}
      {geminiAssessment && (
        <div className="rounded-lg border bg-gray-50 p-3 text-xs text-gray-600">
          <h4 className="mb-1 font-bold text-gray-700">📝 Gemini posudok</h4>
          <p className="italic">{geminiAssessment}</p>
        </div>
      )}
    </div>
  );
};

export default CombinedPanel;
