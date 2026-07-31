/**
 * MeasurementsPanel – displays CEJ to bone crest measurements in mm.
 * Fetches from /results/{job_id}/measurements endpoint.
 */

import { useEffect, useState } from 'react';
import { getMeasurements } from '../hooks/useAnalysis';

type Measurement = {
  tooth_number: string;
  mm: number;
  status: 'normal' | 'mild' | 'moderate' | 'severe';
  note: string;
  label: string;
  point1: number[];
  point2: number[];
};

const STATUS_COLORS: Record<string, { bg: string; text: string; dot: string }> = {
  normal: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', dot: 'bg-emerald-400' },
  mild: { bg: 'bg-amber-500/10', text: 'text-amber-400', dot: 'bg-amber-400' },
  moderate: { bg: 'bg-orange-500/10', text: 'text-orange-400', dot: 'bg-orange-400' },
  severe: { bg: 'bg-red-500/10', text: 'text-red-400', dot: 'bg-red-400' },
};

const STATUS_LABELS: Record<string, string> = {
  normal: 'Normálna',
  mild: 'Mierna',
  moderate: 'Stredná',
  severe: 'Závažná',
};

interface Props {
  jobId: string | null;
  enabled?: boolean;
}

export default function MeasurementsPanel({ jobId, enabled = true }: Props) {
  const [measurements, setMeasurements] = useState<Measurement[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!jobId || !enabled) return;
    
    const fetchMeasurements = async () => {
      setLoading(true);
      try {
        const data = await getMeasurements(jobId);
        if (data?.measurements) {
          setMeasurements(data.measurements);
        }
      } catch (err) {
        console.warn('Failed to fetch measurements:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMeasurements();
  }, [jobId, enabled]);

  if (!enabled || measurements.length === 0) {
    return null;
  }

  return (
    <div className="glass-panel p-4 animate-fade-in">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3 flex items-center gap-2">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-dental-primary">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
        </svg>
        Merania CEJ → Hrebeň kosti
      </h3>
      
      {loading && (
        <div className="text-center py-4 text-dental-textMuted text-xs">
          Načítavam merania...
        </div>
      )}

      {!loading && measurements.length > 0 && (
        <div className="space-y-2">
          {measurements.map((m, idx) => {
            const colors = STATUS_COLORS[m.status] || STATUS_COLORS.normal;
            const label = STATUS_LABELS[m.status] || m.status;
            
            return (
              <div key={idx} className="flex items-center justify-between p-3 rounded-lg border transition-colors hover:bg-slate-700/30">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${colors.dot}`} />
                    <span className={`font-medium text-xs ${colors.text}`}>{label}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {m.tooth_number && (
                      <span className="px-1.5 py-0.5 rounded bg-dental-primary/20 text-dental-primary text-[10px] font-mono font-bold">
                        {m.tooth_number}
                      </span>
                    )}
                    <span className="text-dental-textMuted text-xs truncate max-w-[120px]">
                      {m.label || 'Nález'}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center gap-4 shrink-0">
                  <div className="text-right">
                    <div className="font-mono font-semibold text-dental-primary text-lg">
                      {m.mm.toFixed(1)} mm
                    </div>
                    <div className={`text-[10px] ${colors.text}`}>
                      {STATUS_LABELS[m.status]}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {!loading && measurements.length === 0 && (
        <p className="text-dental-textMuted text-xs text-center py-2">
          Žiadne merania k dispozícii
        </p>
      )}
    </div>
  );
}