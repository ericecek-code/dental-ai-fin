import { useState, useMemo } from 'react';
import { useAnalyze } from '../hooks/useAnalysis';
import UploadZone from '../components/UploadZone';
import CanvasOverlay from '../components/ImageViewer/CanvasOverlay';
import type { ViewMode } from '../components/ImageViewer/CanvasOverlay';
import Controls from '../components/ImageViewer/Controls';
import ProgressTracker from '../components/ProgressTracker';
import Navbar from '../components/Navbar';
import HealthScoreGauge from '../components/HealthScoreGauge';
import FindingCard from '../components/FindingCard';
import Odontogram from '../components/Odontogram';
import { translateClass } from '../lib/labels';

const API_BASE = window.location.origin;

type AnalyzeResult = {
  job_id: string;
  detection_count: number;
  by_class: Record<string, { count: number; max_conf: number; severity: string }>;
  detections: Array<{
    label: string;
    confidence: number;
    bbox: number[];
    severity: string;
    color_bgr: number[];
    tooth_number?: string;
    class_id?: number;
  }>;
  conf_threshold: number;
};

/** Compute health score from detection results (lower findings = higher score) */
function computeHealthScore(result: AnalyzeResult | null): number {
  if (!result || result.detection_count === 0) return 100;

  const total = result.detection_count;
  const urgent = Object.values(result.by_class).filter((v) => v.severity === 'urgent').length;
  const treatSoon = Object.values(result.by_class).filter((v) => v.severity === 'treat_soon').length;

  // Base score starts at 100, deduct for findings
  let score = 100;
  score -= Math.min(total * 3, 40);   // up to -40 for total findings
  score -= urgent * 10;                // -10 per urgent class
  score -= treatSoon * 5;              // -5 per treat_soon class

  return Math.max(0, Math.min(100, Math.round(score)));
}

const Results = () => {
  const [status, setStatus] = useState<string>('idle');
  const [confidence, setConfidence] = useState(0.05);
  const [yoloResult, setYoloResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [viewMode, setViewMode] = useState<ViewMode>('clinical');
  const [imageMode, setImageMode] = useState<'original' | 'enhanced' | 'pseudocolor' | 'heatmap'>('original');
  const [colormap, setColormap] = useState('bone');
  const [hoveredDetection, setHoveredDetection] = useState<number | null>(null);

  const analyze = useAnalyze();

  const handleFile = (file: File) => {
    setError(null);
    setStatus('uploading');
    setYoloResult(null);
    setImageMode('original');

    analyze.mutate(
      { file, conf: confidence },
      {
        onSuccess: (data) => {
          setYoloResult(data as AnalyzeResult);
          setStatus('done');
        },
        onError: (err: any) => {
          setError(err?.response?.data?.detail || err?.message);
          setStatus('error');
        },
      },
    );
  };

  const imageUrl = useMemo(() => {
    if (!yoloResult) return undefined;
    const base = `${API_BASE}/results/${yoloResult.job_id}`;
    switch (imageMode) {
      case 'enhanced': return `${base}/enhanced?ts=${Date.now()}`;
      case 'pseudocolor': return `${base}/pseudocolor?colormap=${colormap}&ts=${Date.now()}`;
      case 'heatmap': return `${base}/heatmap?ts=${Date.now()}`;
      default: return `${base}/original?ts=${Date.now()}`;
    }
  }, [yoloResult, imageMode, colormap]);

  const mappedDetections = useMemo(() => {
    return (yoloResult?.detections || []).map((d) => ({
      ...d,
      class_name: d.label,
      class_id: d.class_id,
    }));
  }, [yoloResult]);

  const healthScore = useMemo(() => computeHealthScore(yoloResult), [yoloResult]);

  return (
    <div className="min-h-screen bg-dental-bg">
      <Navbar />

      <div className="flex flex-col h-[calc(100vh-52px)]">
        {/* Controls bar */}
        <div className="glass-panel-strong border-b border-white/5">
          <Controls
            confidence={confidence}
            onChangeConfidence={setConfidence}
            viewMode={viewMode}
            onChangeViewMode={setViewMode}
            imageMode={imageMode}
            onChangeImageMode={setImageMode}
            colormap={colormap}
            onChangeColormap={setColormap}
          />
        </div>

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

            {/* Image mode shortcuts */}
            {yoloResult && (
              <div className="glass-panel p-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
                  Zobrazenie obrazu
                </h3>
                <div className="space-y-1">
                  {[
                    { key: 'original' as const, label: 'Originál' },
                    { key: 'enhanced' as const, label: 'CLAHE zlepšenie' },
                    { key: 'pseudocolor' as const, label: 'Pseudocolor' },
                    { key: 'heatmap' as const, label: 'Heatmapa' },
                  ].map((m) => (
                    <button
                      key={m.key}
                      onClick={() => setImageMode(m.key)}
                      className={`
                        w-full text-left px-3 py-2 rounded-lg text-[11px] font-medium transition-all duration-200
                        ${imageMode === m.key
                          ? 'bg-dental-primary/15 text-dental-primary'
                          : 'text-dental-textMuted hover:bg-dental-surfaceHighlight/50 hover:text-dental-textMain'
                        }
                      `}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </aside>

          {/* ═══ CENTER CANVAS ═══ */}
          <main className="flex-1 flex flex-col overflow-hidden p-4">
            <div className="glass-panel flex-1 flex flex-col overflow-hidden scan-line-overlay">
              <div className="flex-1 overflow-hidden">
                <CanvasOverlay
                  imageUrl={imageUrl}
                  detections={mappedDetections}
                  viewMode={viewMode}
                />
              </div>
              {/* Bottom info bar */}
              <div className="px-4 py-2 border-t border-white/5 flex items-center justify-between text-[10px] text-dental-textMuted">
                <span>
                  R = boxy · F = kurzor · 0 = reset · koliesko = zoom
                </span>
                <span>
                  {viewMode === 'clinical' ? '🏥 Klinický režim' : '👤 Pacientský režim'}
                </span>
              </div>
            </div>
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

            {/* PDF Export Button */}
            {yoloResult && (
              <a
                className="glass-panel flex items-center justify-center gap-2 p-3 text-sm font-semibold text-dental-primary hover:bg-dental-primary/10 transition-all duration-200 box-glow-teal"
                href={`${API_BASE}/results/${yoloResult.job_id}/report`}
                target="_blank"
                rel="noreferrer"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                  <polyline points="10 9 9 9 8 9" />
                </svg>
                Stiahnuť PDF report
              </a>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
};

export default Results;
