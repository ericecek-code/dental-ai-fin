type AnalysisMode = 'yolo' | 'gemini' | 'combined';

type Props = {
  mode: AnalysisMode;
  onChange: (mode: AnalysisMode) => void;
};

const MODES: { key: AnalysisMode; label: string; icon: string; desc: string }[] = [
  { key: 'yolo', label: 'YOLO', icon: '🔍', desc: 'Rýchla detekcia' },
  { key: 'gemini', label: 'Gemini', icon: '🧠', desc: 'AI sudca' },
  { key: 'combined', label: 'Kombinácia', icon: '⚖️', desc: 'Oba + porovnanie' },
];

const AnalysisModeSelector = ({ mode, onChange }: Props) => {
  return (
    <div className="flex gap-2">
      {MODES.map((m) => (
        <button
          key={m.key}
          type="button"
          onClick={() => onChange(m.key)}
          className={`rounded-lg border px-3 py-2 text-xs font-medium transition-all ${
            mode === m.key
              ? 'border-blue-500 bg-blue-500 text-white shadow-md'
              : 'border-gray-200 bg-white text-gray-600 hover:border-blue-300 hover:bg-blue-50'
          }`}
        >
          <span className="mr-1">{m.icon}</span>
          {m.label}
          <span className={`ml-1 text-[10px] ${mode === m.key ? 'text-blue-100' : 'text-gray-400'}`}>
            {m.desc}
          </span>
        </button>
      ))}
    </div>
  );
};

export default AnalysisModeSelector;
