"use client";

import { useRef, useEffect, useState, useCallback } from "react";

// ─── Types ───────────────────────────────────────────────────────────

export type ViewMode = "clinical" | "patient";

export type DetectionLike = {
  bbox: number[];
  class_id?: number;
  class_name?: string;
  severity?: string;
  confidence?: number;
  tooth_number?: string;
  description?: string;
};

type Props = {
  imageUrl?: string;
  detections?: DetectionLike[];
  heatmapUrl?: string;
  pseudocolorUrl?: string;
  viewMode?: ViewMode;
};

// ─── Helpers ─────────────────────────────────────────────────────────

function getCariesColor(confidence: number): string {
  if (confidence < 0.3) return "#FFD700";
  if (confidence < 0.6) return "#FF8C00";
  return "#FF0000";
}
function getCariesLabel(confidence: number): string {
  if (confidence < 0.3) return "Skorý kaz";
  if (confidence < 0.6) return "Stredný kaz";
  return "Závažný kaz";
}
function getCariesLabelPatient(_confidence: number): string {
  return "Kaz";
}
function getSeverityColor(severity?: string): string {
  if (severity === "urgent") return "#FF0000";
  if (severity === "warning") return "#FFA500";
  return "#00FF00";
}

function drawContour(
  ctx: CanvasRenderingContext2D,
  x: number, y: number, w: number, h: number,
  time: number,
) {
  const seg = 40;
  const wx0 = w * 0.04;
  const wy0 = h * 0.04;
  ctx.beginPath();
  for (let i = 0; i <= seg; i++) {
    const a = (i / seg) * Math.PI * 2;
    const dx = Math.sin(a * 3 + time * 0.001) * wx0 + Math.cos(a * 5 + time * 0.0007) * wx0 * 0.5;
    const dy = Math.cos(a * 4 + time * 0.0012) * wy0 + Math.sin(a * 2 + time * 0.0008) * wy0 * 0.5;
    const px = x + w / 2 + Math.cos(a) * (w / 2 + dx);
    const py = y + h / 2 + Math.sin(a) * (h / 2 + dy);
    if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
  }
  ctx.closePath();
}

// ─── Component ───────────────────────────────────────────────────────

export default function CanvasOverlay({
  imageUrl,
  detections = [],
  heatmapUrl,
  pseudocolorUrl,
  viewMode = "clinical",
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);

  const scaleRef = useRef(1);
  const offsetRef = useRef({ x: 0, y: 0 });
  const dragStartRef = useRef({ x: 0, y: 0 });
  const isDraggingRef = useRef(false);
  const [, forceRender] = useState(0);

  const [showBoxes, setShowBoxes] = useState(true);
  // FIX 1: Default cursor mode changed from "crosshair" to "pan"
  const [cursorMode, setCursorMode] = useState<"pan" | "crosshair">("pan");
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const [heatmapImg, setHeatmapImg] = useState<HTMLImageElement | null>(null);
  const [heatmapOpacity, setHeatmapOpacity] = useState(0.5);
  const [showPseudocolor, setShowPseudocolor] = useState(false);
  const [pseudocolorImg, setPseudocolorImg] = useState<HTMLImageElement | null>(null);

  const animFrameRef = useRef<number>(0);

  // ─── Reset view ────────────────────────────────────────────────────
  const resetView = useCallback(() => {
    const container = containerRef.current;
    const img = imgRef.current;
    if (!container || !img) return;
    const cw = container.clientWidth;
    const ch = container.clientHeight;
    const fit = Math.min(cw / img.naturalWidth, ch / img.naturalHeight) * 0.95;
    scaleRef.current = fit;
    offsetRef.current = {
      x: (cw - img.naturalWidth * fit) / 2,
      y: (ch - img.naturalHeight * fit) / 2,
    };
  }, []);

  // ─── Native wheel handler (blocks page scroll) ─────────────────────
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      e.stopPropagation();
      const container = containerRef.current;
      if (!container || !imgRef.current) return;
      const rect = container.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const factor = e.deltaY < 0 ? 1.1 : 0.9;
      const ns = Math.max(0.1, Math.min(10, scaleRef.current * factor));
      const dx = mx - offsetRef.current.x;
      const dy = my - offsetRef.current.y;
      offsetRef.current = { x: mx - dx * (ns / scaleRef.current), y: my - dy * (ns / scaleRef.current) };
      scaleRef.current = ns;
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, []);

  // ─── Load main image ───────────────────────────────────────────────
  useEffect(() => {
    if (!imageUrl) return;
    setImageLoaded(false);
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      imgRef.current = img;
      resetView();
      setImageLoaded(true);
    };
    img.src = imageUrl;
  }, [imageUrl, resetView]);

  // ─── Load heatmap ──────────────────────────────────────────────────
  useEffect(() => {
    if (!heatmapUrl) { setHeatmapImg(null); return; }
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => setHeatmapImg(img);
    img.src = heatmapUrl;
  }, [heatmapUrl]);

  // ─── Load pseudocolor ──────────────────────────────────────────────
  useEffect(() => {
    if (!pseudocolorUrl) { setPseudocolorImg(null); setShowPseudocolor(false); return; }
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => setPseudocolorImg(img);
    img.src = pseudocolorUrl;
  }, [pseudocolorUrl]);

  // ─── Draw loop ── re-runs when imageLoaded changes ─────────────────
  useEffect(() => {
    if (!imageLoaded) return;
    const canvas = canvasRef.current;
    const img = imgRef.current;
    if (!canvas || !img) return;

    let running = true;

    const draw = () => {
      if (!running) return;
      const ctx = canvas.getContext("2d");
      const container = containerRef.current;
      if (!ctx || !container) { animFrameRef.current = requestAnimationFrame(draw); return; }

      const w = container.clientWidth;
      const h = container.clientHeight;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
      ctx.clearRect(0, 0, w, h);

      const scale = scaleRef.current;
      const off = offsetRef.current;

      // Main image
      ctx.save();
      ctx.translate(off.x, off.y);
      ctx.scale(scale, scale);
      ctx.drawImage(img, 0, 0);
      ctx.restore();

      // Pseudocolor overlay
      if (showPseudocolor && pseudocolorImg) {
        ctx.save();
        ctx.globalAlpha = 0.6;
        ctx.translate(off.x, off.y);
        ctx.scale(scale, scale);
        ctx.drawImage(pseudocolorImg, 0, 0);
        ctx.restore();
      }

      // Heatmap overlay
      if (heatmapImg && showBoxes) {
        ctx.save();
        ctx.globalAlpha = heatmapOpacity;
        ctx.globalCompositeOperation = "screen";
        ctx.translate(off.x, off.y);
        ctx.scale(scale, scale);
        ctx.drawImage(heatmapImg, 0, 0);
        ctx.restore();
      }

      // Detections
      if (showBoxes && detections.length > 0) {
        const now = performance.now();
        for (const det of detections) {
          const [x1, y1, x2, y2] = det.bbox;
          const sx = x1 * scale + off.x;
          const sy = y1 * scale + off.y;
          const sw = (x2 - x1) * scale;
          const sh = (y2 - y1) * scale;

          const conf = det.confidence ?? 0.5;
          const isCaries =
            det.class_name?.toLowerCase().includes("caries") ||
            det.class_name?.toLowerCase().includes("kaz") ||
            (!det.class_name && (det.severity === "urgent" || det.severity === "warning"));

          const color = isCaries ? getCariesColor(conf) : getSeverityColor(det.severity);
          const label = isCaries
            ? (viewMode === "patient" ? getCariesLabelPatient(conf) : getCariesLabel(conf))
            : (det.class_name ?? "Nález");
          const isUrgent = det.severity === "urgent";
          const glowBlur = isUrgent ? 16 * (0.7 + 0.3 * Math.sin(now * 0.004)) : 10;

          ctx.save();
          ctx.shadowColor = color;
          ctx.shadowBlur = glowBlur;
          drawContour(ctx, sx, sy, sw, sh, now);
          ctx.strokeStyle = color;
          ctx.lineWidth = 2.5;
          ctx.stroke();

          // Inner dotted
          ctx.shadowBlur = 0;
          const ins = 4;
          drawContour(ctx, sx + ins, sy + ins, sw - ins * 2, sh - ins * 2, now);
          ctx.setLineDash([4, 4]);
          ctx.strokeStyle = color;
          ctx.lineWidth = 1;
          ctx.stroke();
          ctx.setLineDash([]);

          // Fill
          drawContour(ctx, sx, sy, sw, sh, now);
          ctx.fillStyle = isCaries ? color + (viewMode === "patient" ? "20" : "15") : color + "18";
          ctx.fill();

          // Corners
          const cL = Math.min(10, sw / 5, sh / 5);
          ctx.strokeStyle = color;
          ctx.lineWidth = 3;
          ctx.beginPath(); ctx.moveTo(sx, sy + cL); ctx.lineTo(sx, sy); ctx.lineTo(sx + cL, sy); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(sx + sw - cL, sy); ctx.lineTo(sx + sw, sy); ctx.lineTo(sx + sw, sy + cL); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(sx, sy + sh - cL); ctx.lineTo(sx, sy + sh); ctx.lineTo(sx + cL, sy + sh); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(sx + sw - cL, sy + sh); ctx.lineTo(sx + sw, sy + sh); ctx.lineTo(sx + sw, sy + sh - cL); ctx.stroke();

          // Label
          ctx.font = "bold 11px sans-serif";
          const dLabel = viewMode === "patient" ? label : `${label} ${(conf * 100).toFixed(0)}%`;
          const tm = ctx.measureText(dLabel);
          const pad = 4;
          ctx.fillStyle = color;
          ctx.beginPath(); ctx.roundRect(sx, sy - 22, tm.width + pad * 2, 16, 3); ctx.fill();
          ctx.fillStyle = "#000"; ctx.textBaseline = "middle";
          ctx.fillText(dLabel, sx + pad, sy - 14);

          // Tooth number
          if (det.tooth_number) {
            ctx.font = "bold 10px sans-serif";
            const ttm = ctx.measureText(det.tooth_number);
            const tw = ttm.width + pad * 2;
            const tx = sx + sw - tw;
            const ty = sy - 20;
            ctx.fillStyle = "rgba(0,0,0,0.7)";
            ctx.beginPath(); ctx.roundRect(tx, ty, tw, 14, 3); ctx.fill();
            ctx.strokeStyle = color; ctx.lineWidth = 1;
            ctx.beginPath(); ctx.roundRect(tx, ty, tw, 14, 3); ctx.stroke();
            ctx.fillStyle = "#fff"; ctx.textBaseline = "middle";
            ctx.fillText(det.tooth_number, tx + pad, ty + 7);
          }

          // Severity bar
          if (viewMode === "clinical") {
            const barX = sx - 8;
            ctx.fillStyle = "rgba(255,255,255,0.1)";
            ctx.fillRect(barX, sy, 3, sh);
            ctx.fillStyle = color;
            ctx.fillRect(barX, sy + sh * (1 - conf), 3, sh * conf);
          }

          ctx.restore();
        }
      }

      animFrameRef.current = requestAnimationFrame(draw);
    };

    animFrameRef.current = requestAnimationFrame(draw);
    return () => { running = false; cancelAnimationFrame(animFrameRef.current); };
  }, [imageLoaded, detections, showBoxes, viewMode, heatmapImg, heatmapOpacity, pseudocolorImg, showPseudocolor]);

  // ─── Mouse handlers (use refs, no stale closures) ──────────────────
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      // FIX 2: Allow panning in BOTH modes via middle-click, and always in pan mode
      if (cursorMode === "pan" || e.button === 1) {
        isDraggingRef.current = true;
        dragStartRef.current = { x: e.clientX - offsetRef.current.x, y: e.clientY - offsetRef.current.y };
        forceRender((n) => n + 1); // trigger re-render to update cursor
      }
    },
    [cursorMode],
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!isDraggingRef.current) return;
      offsetRef.current = {
        x: e.clientX - dragStartRef.current.x,
        y: e.clientY - dragStartRef.current.y,
      };
    },
    [],
  );

  const handleMouseUp = useCallback(() => {
    if (isDraggingRef.current) {
      isDraggingRef.current = false;
      forceRender((n) => n + 1); // trigger re-render to update cursor
    }
  }, []);

  // FIX 3: Compute cursor dynamically based on dragging state
  const getCursor = useCallback(() => {
    if (isDraggingRef.current) return "grabbing";
    if (cursorMode === "pan") return "grab";
    return "crosshair";
  }, [cursorMode]);

  // ─── Keyboard shortcuts ────────────────────────────────────────────
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement).tagName === "INPUT") return;
      if (e.key === "Escape") {
        if (isFullscreen) document.exitFullscreen?.();
      } else if (e.key === "r" || e.key === "R") {
        setShowBoxes((p) => !p);
      } else if (e.key === "f" || e.key === "F") {
        setCursorMode((p) => (p === "pan" ? "crosshair" : "pan"));
      } else if (e.key === "0") {
        resetView();
        forceRender((n) => n + 1);
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isFullscreen, resetView]);

  // ─── Fullscreen ────────────────────────────────────────────────────
  useEffect(() => {
    const onFsChange = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", onFsChange);
    return () => document.removeEventListener("fullscreenchange", onFsChange);
  }, []);

  const toggleFullscreen = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    if (isFullscreen) document.exitFullscreen?.();
    else el.requestFullscreen?.();
  }, [isFullscreen]);

  // ─── Render ────────────────────────────────────────────────────────
  return (
    <div
      ref={containerRef}
      className="relative w-full bg-black overflow-hidden"
      style={{
        cursor: getCursor(),
        minHeight: 500,
      }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />

      {/* Placeholder when no image */}
      {!imageLoaded && (
        <div className="absolute inset-0 flex items-center justify-center text-gray-500 text-sm">
          Nahrajte RTG snímku
        </div>
      )}

      {/* Toolbar */}
      <div className="absolute top-3 right-3 z-20 flex flex-col gap-2 items-end">
        <button
          onClick={toggleFullscreen}
          className="bg-gray-800/80 hover:bg-gray-700 text-white px-3 py-1.5 rounded text-xs font-medium backdrop-blur-sm border border-gray-700/50"
          title={isFullscreen ? "Opustiť celú obrazovku (Esc)" : "Celá obrazovka"}
        >
          {isFullscreen ? "✕ Zavrieť" : "⛶ Celá obrazovka"}
        </button>

        {/* FIX 4: Added visible Pan/Crosshair toggle button */}
        <button
          onClick={() => setCursorMode((p) => (p === "pan" ? "crosshair" : "pan"))}
          className={`px-3 py-1.5 rounded text-xs font-medium backdrop-blur-sm border border-gray-700/50 transition-colors ${
            cursorMode === "pan"
              ? "bg-blue-600 text-white"
              : "bg-gray-800/80 text-gray-300 hover:bg-gray-700"
          }`}
          title="Prepnúť medzi posúvaním a zameriavaním (F)"
        >
          {cursorMode === "pan" ? "✋ Posúvanie" : "⊕ Zameriavanie"}
        </button>

        <div className="flex rounded-lg overflow-hidden border border-gray-700/60 backdrop-blur-sm">
          <span className="px-2 py-1 text-[10px] text-gray-400 bg-gray-800/80">
            {viewMode === "clinical" ? "Klinický" : "Pacientský"}
          </span>
        </div>

        {pseudocolorImg && (
          <button
            onClick={() => setShowPseudocolor((p) => !p)}
            className={`px-3 py-1.5 rounded text-xs font-medium backdrop-blur-sm border border-gray-700/50 transition-colors ${
              showPseudocolor ? "bg-purple-600 text-white" : "bg-gray-800/80 text-gray-300 hover:bg-gray-700"
            }`}
          >
            {showPseudocolor ? "Skryť pseudo" : "Pseudocolor"}
          </button>
        )}

        {heatmapImg && (
          <div className="bg-gray-800/80 backdrop-blur-sm border border-gray-700/50 rounded px-2 py-1.5 flex items-center gap-2">
            <span className="text-[10px] text-gray-400">Heatmap</span>
            <input
              type="range" min={0} max={1} step={0.05}
              value={heatmapOpacity}
              onChange={(e) => setHeatmapOpacity(parseFloat(e.target.value))}
              className="w-20 accent-fuchsia-500"
            />
          </div>
        )}
      </div>

      {/* FIX 5: Help tooltip at bottom-left showing keyboard shortcuts */}
      <div className="absolute bottom-3 left-3 z-20 bg-gray-800/80 backdrop-blur-sm border border-gray-700/50 rounded px-3 py-1.5 text-[10px] text-gray-400">
        <span className="mr-3">🖱️ Ťahaj pre posúvanie</span>
        <span className="mr-3">🔍 Koliesko pre zoom</span>
        <span className="mr-3">F – prepni mód</span>
        <span className="mr-3">R – schovaj boxy</span>
        <span>0 – reset pohľad</span>
      </div>
    </div>
  );
}
