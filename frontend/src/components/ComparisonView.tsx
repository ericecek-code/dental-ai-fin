import { useState, useRef, useCallback, useEffect } from 'react';

type ComparisonViewProps = {
  originalUrl?: string;
  enhancedUrl?: string;
  detections?: any[];
};

export default function ComparisonView({ originalUrl, enhancedUrl, detections }: ComparisonViewProps) {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      const pct = Math.max(0, Math.min(100, (x / rect.width) * 100));
      setSliderPosition(pct);
    },
    [],
  );

  useEffect(() => {
    if (!isDragging) return;

    const onMouseMove = (e: MouseEvent) => handleMove(e.clientX);
    const onTouchMove = (e: TouchEvent) => handleMove(e.touches[0].clientX);
    const onUp = () => setIsDragging(false);

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onUp);
    window.addEventListener('touchmove', onTouchMove);
    window.addEventListener('touchend', onUp);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onUp);
      window.removeEventListener('touchmove', onTouchMove);
      window.removeEventListener('touchend', onUp);
    };
  }, [isDragging, handleMove]);

  if (!originalUrl && !enhancedUrl) return null;

  return (
    <div className="glass-panel rounded-2xl p-4 relative overflow-hidden">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
        Porovnanie snímok
      </h3>

      <div
        ref={containerRef}
        className="relative h-96 bg-black rounded-lg overflow-hidden cursor-ew-resize select-none"
        onMouseDown={(e) => {
          setIsDragging(true);
          handleMove(e.clientX);
        }}
        onTouchStart={(e) => {
          setIsDragging(true);
          handleMove(e.touches[0].clientX);
        }}
      >
        {/* Original image (left side) */}
        {originalUrl && (
          <img
            src={originalUrl}
            alt="Originál"
            className="absolute inset-0 w-full h-full object-contain"
            style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
            draggable={false}
          />
        )}

        {/* Enhanced image with detection overlay (right side) */}
        {enhancedUrl && (
          <img
            src={enhancedUrl}
            alt="Vylepšená"
            className="absolute inset-0 w-full h-full object-contain"
            style={{ clipPath: `inset(0 0 0 ${sliderPosition}%)`, opacity: 0.85 }}
            draggable={false}
          />
        )}

        {/* Slider handle */}
        <div
          className="absolute top-0 bottom-0 w-0.5 cursor-ew-resize"
          style={{ left: `${sliderPosition}%`, backgroundColor: '#14b8a6' }}
          onMouseDown={(e) => {
            e.stopPropagation();
            setIsDragging(true);
          }}
          onTouchStart={(e) => {
            e.stopPropagation();
            setIsDragging(true);
          }}
        >
          <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-dental-primary border-2 border-white flex items-center justify-center shadow-lg shadow-dental-primary/40">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" className="-ml-3">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
        </div>

        {/* Labels */}
        <div className="absolute top-3 left-3 px-2 py-1 rounded bg-black/60 text-[10px] font-semibold text-white uppercase tracking-wider">
          Originál
        </div>
        <div className="absolute top-3 right-3 px-2 py-1 rounded bg-dental-primary/80 text-[10px] font-semibold text-white uppercase tracking-wider">
          Vylepšená
        </div>
      </div>

      <p className="text-[10px] text-dental-textMuted mt-2 text-center">
        Posuňte delič pre porovnanie originálu a vylepšenej snímky
      </p>
    </div>
  );
}
