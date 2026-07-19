import { useState, useMemo } from 'react';
import { useAnalyze } from '../hooks/useAnalysis';
import UploadZone from '../components/UploadZone';
import CanvasOverlay from '../components/ImageViewer/CanvasOverlay';
import type { ViewMode } from '../components/ImageViewer/CanvasOverlay';
import ColorLegend from '../components/ImageViewer/ColorLegend';
import DetectionCard from '../components/ImageViewer/DetectionCard';
import Controls from '../components/ImageViewer/Controls';
import ReportPanel from '../components/ReportPanel';
import ProgressTracker from '../components/ProgressTracker';
import { translateClass, translateSeverity } from '../lib/labels';

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

const Results = () => {
  const [status, setStatus] = useState<string>('idle');
  const [confidence, setConfidence] = useState(0.05);
  const [yoloResult, setYoloResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // New: view mode & image mode
  const [viewMode, setViewMode] = useState<ViewMode>('clinical');
  const [imageMode, setImageMode] = useState<'original' | 'enhanced' | 'pseudocolor' | 'heatmap'>('original');
  const [colormap, setColormap] = useState('bone');

  const analyze = useAnalyze();

  const handleFile = (file: File) => {
    setError(null);
    setStatus('uploading');
    setYoloResult(null);
    setImageMode('original');

    analyze.mutate(
      { file, conf: confidence },
      {
        onSuccess: (data) => { setYoloResult(data as AnalyzeResult); setStatus('done'); },
        onError: (err: any) => { setError(err?.response?.data?.detail || err?.message); setStatus('error'); },
      },
    );
  };

  // Dynamic image URL based on mode
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

  // Map detections to include class_name for CanvasOverlay
  const mappedDetections = useMemo(() => {
    return (yoloResult?.detections || []).map(d => ({
      ...d,
      class_name: d.label,
      class_id: d.class_id,
    }));
  }, [yoloResult]);

  return (
    <div className="mx-auto max-w-6xl p-4">
      <h1 className="mb-4 text-2xl font-bold">Dental AI</h1>

      <div className="mb-4">
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

      <UploadZone onFile={handleFile} />

      <div className="mt-4">
        <ProgressTracker step={status} />
      </div>

      {error && (
        <div className="mt-2 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>
      )}

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <CanvasOverlay
            imageUrl={imageUrl}
            detections={mappedDetections}
            viewMode={viewMode}
          />
          <p className="mt-1 text-[10px] text-gray-400">
            R = boxy · F = kurzor · 0 = reset · koliesko = zoom ·
            {viewMode === 'clinical' ? ' Klinický režim' : ' Pacientský režim'}
          </p>
        </div>
        <div className="space-y-4">
          <ColorLegend />
          <DetectionCard detections={yoloResult?.detections || []} />
          {yoloResult && (
            <div className="rounded-md border bg-white p-3 text-xs">
              <h3 className="mb-1 text-sm font-semibold">Štatistika</h3>
              {Object.entries(yoloResult.by_class).map(([cls, v]) => (
                <div key={cls} className="flex justify-between border-b py-1 last:border-b-0">
                  <span>{translateClass(cls)}</span>
                  <span>{v.count}× · {(v.max_conf * 100).toFixed(1)}% · {translateSeverity(v.severity)}</span>
                </div>
              ))}
            </div>
          )}
          {yoloResult && (
            <a
              className="block rounded-md border bg-white p-3 text-center text-xs text-blue-700"
              href={`${API_BASE}/results/${yoloResult.job_id}/report`}
              target="_blank" rel="noreferrer"
            >
              Stiahnuť PDF report
            </a>
          )}
          <ReportPanel />
        </div>
      </div>
    </div>
  );
};

export default Results;
