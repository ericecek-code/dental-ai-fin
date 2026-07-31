import { useState } from 'react';
import { translateClass } from '../lib/labels';

type Annotation = {
  id: string;
  tooth_number: string;
  text: string;
  created_at: string;
};

type AnnotationsProps = {
  detections: any[];
  onSave: (annotations: Annotation[]) => void;
};

export default function Annotations({ detections, onSave }: AnnotationsProps) {
  const [annotations, setAnnotations] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState(false);

  const detectionsWithTooth = detections.filter((d) => d.tooth_number && d.tooth_number !== '?');

  if (detectionsWithTooth.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
          Poznámky k nálezom
        </h3>
        <p className="text-[11px] text-dental-textMuted text-center py-2">
          Žiadne nálezy s priradeným zubom
        </p>
      </div>
    );
  }

  const handleSave = () => {
    const result = Object.entries(annotations)
      .filter(([_, text]) => text.trim())
      .map(([tooth, text]) => ({
        id: crypto.randomUUID(),
        tooth_number: tooth,
        text,
        created_at: new Date().toISOString(),
      }));
    onSave(result);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="glass-panel rounded-2xl p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
        Poznámky k nálezom
      </h3>
      <div className="space-y-2">
        {detectionsWithTooth.map((det, i) => {
          const sk = translateClass(det.label);
          return (
            <div key={i} className="flex items-center gap-2">
              <span className="shrink-0 w-8 h-8 rounded-lg bg-dental-primary/20 flex items-center justify-center text-[10px] font-mono font-bold text-dental-primary">
                {det.tooth_number}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-[10px] text-dental-textMuted truncate">{sk}</p>
                <input
                  type="text"
                  placeholder="Poznámka..."
                  value={annotations[det.tooth_number] || ''}
                  onChange={(e) =>
                    setAnnotations((prev) => ({
                      ...prev,
                      [det.tooth_number]: e.target.value,
                    }))
                  }
                  className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-dental-primary transition-colors"
                />
              </div>
            </div>
          );
        })}
      </div>
      <button
        onClick={handleSave}
        className={`mt-3 w-full py-2 rounded-lg text-xs font-medium transition-all duration-200 ${
          saved
            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
            : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
        }`}
      >
        {saved ? '✓ Uložené' : 'Uložiť poznámky'}
      </button>
    </div>
  );
}
