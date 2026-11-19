import { useState, useMemo } from 'react';
import { useAnalyze } from '../hooks/useAnalysis';
import UploadZone from '../components/UploadZone';
import ProgressTracker from '../components/ProgressTracker';
import Navbar from '../components/Navbar';
import HealthScoreGauge from '../components/HealthScoreGauge';
import FindingCard from '../components/FindingCard';
import Odontogram from '../components/Odontogram';
import Annotations from '../components/Annotations';
import HistoryPanel from '../components/HistoryPanel';
import MeasurementsPanel from '../components/MeasurementsPanel';
import { translateClass } from '../lib/labels';

const API_BASE = window.location.origin;

type AnalyzeResult = {
  job_id: string;
  detection_count: number;
  health_score?: number;
  by_class: Record<string, { count: number; max_conf: number; severity: string }>;
  detections: Array<{
    label: string;
    label_sk?: string;
    confidence: number;
    bbox: number[];
    severity: string;
    color_bgr: number[];
    tooth_number?: string;
    class_id?: number;
  }>;
  conf_threshold: number;
  filename?: string;
  privacy?: { anonymized: boolean; removed?: string[]; reason?: string };
};

/** Health score comes from the backend (0..1) — the UI only scales it. */
function computeHealthScore(result: AnalyzeResult | null): number {
  if (!result) return 100;
  const raw = result.health_score;
  if (typeof raw === 'number' && Number.isFinite(raw)) {
    return Math.max(0, Math.min(100, Math.round(raw * 100)));
  }
  return 100;
}

/** Download a file through fetch so auth headers can be attached. */
async function downloadFile(url: string, filename: string) {
  const token = localStorage.getItem('api_token');
  const response = await fetch(url, {
    headers: token ? { 'X-API-Key': token } : undefined,
  });
  if (!response.ok) {
    throw new Error(`Export failed: HTTP ${response.status}`);
  }
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}

const Results = () => {
  const [status, setStatus] = useState<string>('idle');
  const [yoloResult, setYoloResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [, setHoveredDetection] = useState<number | null>(null);

  const analyze = useAnalyze();

  const handleFile = (file: File) => {
    setError(null);
    setStatus('uploading');
    setYoloResult(null);

    analyze.mutate(
      { file, conf: 0.05 },
      {
        onSuccess: (data) => {
          setYoloResult(data as AnalyzeResult);
          setStatus('done');
        },
        onError: (err: unknown) => {
          const e = err as { response?: { data?: { detail?: string } }; message?: string };
          setError(e?.response?.data?.detail || e?.message || 'Analýza zlyhala');
          setStatus('error');
        },
      },
    );
  };

  const healthScore = useMemo(() => computeHealthScore(yoloResult), [yoloResult]);

  // Export handlers — idú cez fetch, aby fungovali aj s API_TOKEN
  const handleExportJson = () => {
    if (!yoloResult) return;
    downloadFile(`${API_BASE}/results/${yoloResult.job_id}/json`, `${yoloResult.job_id}.json`)
      .catch((err) => setError(err.message));
  };

  const handleExportCsv = () => {
    if (!yoloResult) return;
    downloadFile(`${API_BASE}/results/${yoloResult.job_id}/csv`, `${yoloResult.job_id}.csv`)
      .catch((err) => setError(err.message));
  };

  const handleSaveAnnotations = (annotations: unknown[]) => {
    // Store annotations (could be sent to backend in future)
    console.log('Saved annotations:', annotations);
  };

  return (
    <div className="min-h-screen bg-dental-bg">
      <Navbar />

      <div className="flex flex-col h-[calc(100vh-52px)]">

        {/* Main 3-column layout */}
        <div className="flex-1 flex overflow-hidden">

          {/* ═══ LEFT SIDEBAR (280px) ═══ */}
          <aside className="w-[280px] shrink-0 border-r border-white/5 overflow-y-auto p-4 space-y-4">
            {/* Upload zone */}
            <UploadZone onFile={handleFile} />

            {/* Progress */}
            <ProgressTracker step={status} />

            {/* Error */}
            {error && (
              <div className="rounded-lg border border-status-caries/30 bg-status-caries/10 p-3 text-xs text-status-caries animate-fade-in">
                {error}
              </div>
            )}

            {/* Recent scans placeholder */}
            <div className="glass-panel p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
                Posledné snímky
              </h3>
              {yoloResult ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-3 p-2 rounded-lg bg-dental-primary/10 border border-dental-primary/20">
                    <div className="w-8 h-8 rounded bg-dental-primary/20 flex items-center justify-center">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0D9488" strokeWidth="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" />
                        <circle cx="8.5" cy="8.5" r="1.5" />
                        <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
                      </svg>
                    </div>
                    <div className="min-w-0">
                      <p className="text-[11px] font-medium text-dental-textMain truncate">
                        {translateClass(yoloResult.detections[0]?.label || '') || 'Snímka'}
                      </p>
                      <p className="text-[10px] text-dental-textMuted">
                        {yoloResult.detection_count} nálezov
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-[11px] text-dental-textMuted text-center py-2">
                  Žiadne snímky
                </p>
              )}
            </div>

            {/* Export buttons */}
            {yoloResult && (
              <div className="glass-panel p-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
                  Export
                </h3>
                {yoloResult.privacy?.anonymized ? (
                  <p className="mb-3 flex items-start gap-2 rounded-lg bg-emerald-500/10 px-2.5 py-2 text-[10px] leading-snug text-emerald-300">
                    <span aria-hidden>🛡️</span>
                    <span>
                      Osobné údaje odstránené — metadáta, DICOM identifikátory a názov súboru.
                    </span>
                  </p>
                ) : (
                  <p className="mb-3 flex items-start gap-2 rounded-lg bg-amber-500/10 px-2.5 py-2 text-[10px] leading-snug text-amber-300">
                    <span aria-hidden>⚠️</span>
                    <span>Osobné údaje neboli odstránené (anonymizácia vypnutá).</span>
                  </p>
                )}
                <div className="space-y-2">
                  <button
                    onClick={handleExportJson}
                    className="w-full flex items-center justify-center gap-2 p-2.5 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-[11px] font-medium text-slate-300 hover:text-white transition-all duration-200"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="7 10 12 15 17 10" />
                      <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                    Stiahnuť JSON
                  </button>
                  <button
                    onClick={handleExportCsv}
                    className="w-full flex items-center justify-center gap-2 p-2.5 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-[11px] font-medium text-slate-300 hover:text-white transition-all duration-200"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="7 10 12 15 17 10" />
                      <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                    Stiahnuť CSV
                  </button>
                </div>
              </div>
            )}

            {/* History panel */}
            <HistoryPanel />
          </aside>

          {/* ═══ CENTER: Výsledky analýzy (snímka bola vymazaná) ═══ */}
          <main className="flex-1 flex flex-col overflow-hidden p-4">
            {yoloResult ? (
              <div className="glass-panel-strong flex-1 flex flex-col items-center justify-center text-center p-8">
                <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-dental-textMain mb-2">Snímka bola vymazaná</h3>
                <p className="text-dental-textMuted max-w-md mx-auto mb-6">
                  V intérêtoch ochrany súkromia pacienta bola RTG snímka a všetky
                  generované obrázky (overlay, enhanced, heatmap) po analýze trvalo
                  odstránené zo serveru. PDF report je generovaný bez vloženého
                  obrázka — obsahuje len textovú tabuľku nálezov.
                </p>
                <div className="glass-panel p-4 w-full max-w-md">
                  <h4 className="text-xs font-semibold text-dental-textMuted uppercase tracking-wider mb-3">Detekované nálezy</h4>
                  <div className="space-y-2">
                    {yoloResult.detections.map((d, i) => (
                      <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-slate-800/50 text-sm">
                        <span className={`w-2 h-2 rounded-full shrink-0 mt-0.5 ${d.severity === 'urgent' ? 'bg-rose-400' : d.severity === 'treat_soon' ? 'bg-amber-400' : 'bg-emerald-400'}`} />
                        <div className="flex-1">
                          <div className="flex justify-between text-[11px]">
                            <span className="text-dental-textMain font-medium">{d.label_sk || d.label}</span>
                            <span className="text-dental-textMuted font-mono">{Math.round(d.confidence * 100)}%</span>
                          </div>
                          {d.tooth_number && (
                            <div className="text-[10px] text-dental-textMuted">Zub: {d.tooth_number}</div>
                          )}
                        </div>
                      </div>
                    ))}
                    {yoloResult.detections.length === 0 && (
                      <p className="text-[11px] text-dental-textMuted text-center py-2">Žiadne nálezy</p>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
                <div className="w-16 h-16 rounded-full bg-cyan-500/10 flex items-center justify-center mx-auto mb-4">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0EA5E9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-dental-textMain mb-2">Pripravený na analýzu</h3>
                <p className="text-dental-textMuted max-w-sm mx-auto">
                  Nahrajte panoramatický RTG snímku. Po analýze bude snímka trvalo
                  odstránená zo serveru (ochrana súkromia).
                </p>
              </div>
            )}
          </main>

          {/* ═══ RIGHT PANEL (320px) ═══ */}
          <aside className="w-[320px] shrink-0 border-l border-white/5 overflow-y-auto p-4 space-y-4">
            {/* Health Score Gauge */}
            <HealthScoreGauge score={healthScore} />

            {/* Findings list */}
            <FindingCard
              detections={yoloResult?.detections || []}
              onHoverIndex={setHoveredDetection}
            />

            {/* Statistics panel */}
            {yoloResult && Object.keys(yoloResult.by_class).length > 0 && (
              <div className="glass-panel p-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
                  Štatistika
                </h3>
                <div className="space-y-2">
                  {Object.entries(yoloResult.by_class).map(([cls, v]) => (
                    <div
                      key={cls}
                      className="flex items-center justify-between text-[11px] py-1.5 border-b border-white/5 last:border-b-0"
                    >
                      <span className="text-dental-textMain font-medium">
                        {translateClass(cls)}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-dental-textMuted">
                          {v.count}×
                        </span>
                        <span className="font-mono font-semibold text-dental-primary">
                          {(v.max_conf * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Odontogram */}
            <Odontogram findings={yoloResult?.detections || []} />

            {/* Annotations panel */}
                        <Annotations
                          detections={yoloResult?.detections || []}
                          onSave={handleSaveAnnotations}
                        />

                        {/* Measurements panel */}
                        <MeasurementsPanel jobId={yoloResult?.job_id || null} enabled={!!yoloResult} />

                        {/* PDF Export Button */}
                        {yoloResult && (
                          <button
                            type="button"
                            className="glass-panel flex items-center justify-center gap-2 p-3 text-sm font-semibold text-dental-primary hover:bg-dental-primary/10 transition-all duration-200 box-glow-teal"
                            onClick={() => {
                              downloadFile(
                                `${API_BASE}/results/${yoloResult.job_id}/report`,
                                `${yoloResult.job_id}.pdf`,
                              ).catch((err) => setError(err.message));
                            }}
                          >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                              <polyline points="14 2 14 8 20 8" />
                              <line x1="16" y1="13" x2="8" y2="13" />
                              <line x1="16" y1="17" x2="8" y2="17" />
                              <polyline points="10 9 9 9 8 9" />
                            </svg>
                            Stiahnuť PDF report
                          </button>
                        )}

                        {/* AI Disclaimer */}
                        {yoloResult && (
                          <div className="glass-panel-strong border border-status-watch/30 bg-status-watch/5 p-3 rounded-lg">
                            <div className="flex items-start gap-2">
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-status-watch shrink-0 mt-0.5">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="12" y1="8" x2="12" y2="12" />
                                <line x1="12" y1="16" x2="12.01" y2="16" />
                              </svg>
                              <p className="text-[10px] text-dental-textMuted leading-relaxed">
                                <span className="font-medium text-status-watch">Dôležité:</span> AI podporný nástroj – nenahrádza klinické posúdenie zubného lekára.
                                Všetky nálezy sú len orientačné a vyžadujú odbornú validáciu.
                              </p>
                            </div>
                          </div>
                        )}
                      </aside>
        </div>
      </div>
    </div>
  );
};

export default Results;
