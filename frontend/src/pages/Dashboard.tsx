import { useState } from 'react';
import UploadZone from '../components/UploadZone';
import CanvasOverlay from '../components/ImageViewer/CanvasOverlay';
import type { ViewMode } from '../components/ImageViewer/CanvasOverlay';
import ColorLegend from '../components/ImageViewer/ColorLegend';
import DetectionCard from '../components/ImageViewer/DetectionCard';
import Controls from '../components/ImageViewer/Controls';
import ReportPanel from '../components/ReportPanel';
import ProgressTracker from '../components/ProgressTracker';

const Dashboard = () => {
  const [status, setStatus] = useState<string>('idle');
  const [confidence, setConfidence] = useState(0.5);
  const [viewMode, setViewMode] = useState<ViewMode>('clinical');
  const [imageMode, setImageMode] = useState<'original' | 'enhanced' | 'pseudocolor' | 'heatmap'>('original');
  const [colormap, setColormap] = useState('bone');

  return (
    <div className="mx-auto max-w-6xl p-4">
      <h1 className="mb-4 text-2xl font-bold">Dental AI</h1>
      <UploadZone onFile={(file) => {
        console.log('Upload', file);
        setStatus('queued');
      }} />
      <div className="mt-4">
        <ProgressTracker step={status} />
      </div>
      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <CanvasOverlay viewMode={viewMode} />
        </div>
        <div className="space-y-4">
          <ColorLegend />
          <DetectionCard detections={[]} />
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
          <ReportPanel />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
