"use client";

import { useState, useRef } from 'react';
import Navbar from '../components/Navbar';

type UploadZoneHandle = {
  openFilePicker: () => void;
};
import CanvasOverlay from '../components/ImageViewer/CanvasOverlay';
import type { ViewMode } from '../components/ImageViewer/CanvasOverlay';
import ColorLegend from '../components/ImageViewer/ColorLegend';
import DetectionCard from '../components/ImageViewer/DetectionCard';
import Controls from '../components/ImageViewer/Controls';
import ReportPanel from '../components/ReportPanel';
import ToastSystem from '../components/ToastSystem';

type Detection = {
  label: string;
  confidence: number;
  bbox: number[];
  tooth_number?: string;
  severity?: string;
};

const Dashboard = () => {
  const uploadZoneRef = useRef<UploadZoneHandle>(null);

  const [status, setStatus] = useState<'idle' | 'uploading' | 'analyzing' | 'done' | 'error'>('idle');
  const [confidence, setConfidence] = useState(0.25);
  const [viewMode, setViewMode] = useState<ViewMode>('clinical');
  const [imageMode, setImageMode] = useState<'original' | 'enhanced' | 'pseudocolor' | 'heatmap'>('original');
  const [colormap, setColormap] = useState('bone');
  const [detections, setDetections] = useState<Detection[]>([]);
  const [healthScore, setHealthScore] = useState<number | null>(null);
  const [filename, setFilename] = useState<string | null>(null);

  const handleOpenPicker = () => {
    uploadZoneRef.current?.openFilePicker();
  };

  const handleReset = () => {
    setStatus('idle');
    setFilename(null);
    setDetections([]);
    setHealthScore(null);
  };

  return (
    <div className="min-h-screen bg-dental-background text-dental-textMain">
      <ToastSystem />
      <Navbar />

      <main className="mx-auto max-w-7xl px-4 py-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold text-dental-textMain">Analýza RTG snímky</h2>
            <p className="text-dental-textMuted text-sm">
              Automatická detekcia kazu, implantátov a patológií cez YOLOv8
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleOpenPicker}
              disabled={status === 'uploading' || status === 'analyzing'}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                status === 'uploading' || status === 'analyzing'
                  ? 'bg-dental-primary/50 text-dental-textMuted cursor-not-allowed'
                  : 'bg-dental-primary hover:bg-dental-primary/90 text-white'
              }`}
            >
              {status === 'uploading' ? (
                <span className="flex items-center gap-2">
                  <span className="spinner" />
                  Nahrávanie...
                </span>
              ) : status === 'analyzing' ? (
                <span className="flex items-center gap-2">
                  <span className="spinner" />
                  Analýza prebehne...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  Nahrať nový snímok
                </span>
              )}
            </button>
            {filename && (
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-dental-surfaceHover hover:bg-dental-primary/20 text-dental-textMain border border-dental-border rounded-lg text-sm font-medium transition-colors"
              >
                Reset
              </button>
            )}
          </div>
        </div>

        {/* Stats Row (only when analysis done) */}
        {status === 'done' && detections.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="glass-panel p-4">
              <div className="text-xs text-dental-textMuted uppercase font-semibold tracking-wider mb-1">Detekované nálezy</div>
              <div className="text-2xl font-bold text-dental-textMain">{detections.length}</div>
            </div>
            <div className="glass-panel p-4">
              <div className="text-xs text-dental-textMuted uppercase font-semibold tracking-wider mb-1">Health Score</div>
              <div className="text-2xl font-bold">
                {healthScore !== null ? (
                  <span className={healthScore >= 70 ? "text-emerald-400" : healthScore >= 40 ? "text-amber-400" : "text-rose-400"}>
                    {Math.round(healthScore)}/100
                  </span>
                ) : (
                  <span className="text-dental-textMuted">--</span>
                )}
              </div>
            </div>
            <div className="glass-panel p-4">
              <div className="text-xs text-dental-textMuted uppercase font-semibold tracking-wider mb-1">Prahový filter</div>
              <div className="text-2xl font-bold text-cyan-400">{Math.round(confidence * 100)}%</div>
            </div>
            <div className="glass-panel p-4">
              <div className="text-xs text-dental-textMuted uppercase font-semibold tracking-wider mb-1">Snímok</div>
              <div className="text-sm font-medium text-dental-textMain truncate">{filename}</div>
            </div>
          </div>
        )}

        {/* Status indicator */}
        {status === 'error' && (
          <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center gap-3">
            <span className="text-rose-400">⚠</span>
            <span className="text-sm text-rose-200">Analýza zlyhala. Skúste znova alebo skontrolujte formát snímku.</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Image Viewer (8 cols) */}
          <div className="lg:col-span-8 space-y-4">
            <div className="glass-panel-strong p-1">
              <CanvasOverlay viewMode={viewMode} />
            </div>
            <div className="flex gap-2">
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
          </div>

          {/* Right: Sidebar (4 cols) */}
          <div className="lg:col-span-4 space-y-4">
            <ColorLegend />
            <DetectionCard detections={detections} />
            <MeasurementsPanelPreview detections={detections} healthScore={healthScore} />
            <ReportPanel />
          </div>
        </div>

        {status === 'idle' && !filename && (
          <div className="mt-8 glass-panel-strong p-8 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-cyan-500/10 mx-auto mb-4">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#0EA5E9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-dental-textMain mb-2">Pripravený na analýzu</h3>
            <p className="text-dental-textMuted max-w-sm mx-auto">
              Nahrajte panoramatický RTG snímku a Dental AI automaticky detekuje kariés, implantáty, cysty a inú patológiu.
            </p>
          </div>
        )}
      </main>
    </div>
  );
};

function MeasurementsPanelPreview({ detections, healthScore }: { detections: Detection[]; healthScore: number | null }) {
  if (detections.length === 0) return null;

  const urgent = detections.filter((d) => d.severity === "urgent").length;
  const treatSoon = detections.filter((d) => d.severity === "treat_soon").length;
  const watch = detections.filter((d) => d.severity === "watch").length;

  return (
    <div className="glass-panel p-4">
      <h3 className="text-xs font-semibold text-dental-textMuted uppercase tracking-wider mb-3">Prehľad závažnosti</h3>
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-dental-textMuted">Okamžité riešenie</span>
          <span className={`font-medium ${urgent > 0 ? "text-rose-400" : "text-dental-textMuted"}`}>{urgent}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-dental-textMuted">Ošetriť čoskoro</span>
          <span className={`font-medium ${treatSoon > 0 ? "text-amber-400" : "text-dental-textMuted"}`}>{treatSoon}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-dental-textMuted">Sledovať</span>
          <span className={`font-medium ${watch > 0 ? "text-cyan-400" : "text-dental-textMuted"}`}>{watch}</span>
        </div>
      </div>
      {healthScore !== null && (
        <div className="mt-4 pt-4 border-t border-dental-border">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-dental-textMuted">Celkový health score</span>
            <span className="font-bold text-dental-textMain">{Math.round(healthScore)}/100</span>
          </div>
          <div className="w-full bg-dental-surfaceHighlight rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-1000 ${
                healthScore >= 70 ? "bg-emerald-500" : healthScore >= 40 ? "bg-amber-500" : "bg-rose-500"
              }`}
              style={{ width: `${Math.max(0, Math.min(100, healthScore))}%` }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;