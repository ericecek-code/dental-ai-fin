import type { ViewMode } from "./CanvasOverlay";

export type { ViewMode };

type Props = {
  confidence: number;
  onChangeConfidence: (value: number) => void;
  viewMode: ViewMode;
  onChangeViewMode: (mode: ViewMode) => void;
  imageMode: "original" | "enhanced" | "pseudocolor" | "heatmap";
  onChangeImageMode: (
    mode: "original" | "enhanced" | "pseudocolor" | "heatmap"
  ) => void;
  colormap?: string;
  onChangeColormap?: (cmap: string) => void;
};

const IMAGE_MODES = [
  { key: "original" as const, label: "Originál" },
  { key: "enhanced" as const, label: "CLAHE" },
  { key: "pseudocolor" as const, label: "Pseudocolor" },
  { key: "heatmap" as const, label: "Heatmap" },
];

const COLORMAPS = [
  { key: "bone", label: "Bone" },
  { key: "inferno", label: "Inferno" },
  { key: "jet", label: "Jet" },
  { key: "magma", label: "Magma" },
];

const SENSITIVITY_INFO: Record<string, { label: string; color: string; desc: string }> = {
  ultra: { label: 'Ultra citlivá', color: 'text-red-600', desc: 'Všetky nálezy vrátane neistých. Veľa detekcií, zachytí aj mikro kazy.' },
  high: { label: 'Vysoká (odporúčaná)', color: 'text-green-600', desc: 'Najlepší pomer presnosť/množstvo. Zachytí 92% nálezov s rozumným počtom detekcií.' },
  medium: { label: 'Stredná', color: 'text-yellow-600', desc: 'Isté nálezy, menej detekcií. Môže prehliadať jemné kazy.' },
  low: { label: 'Nízka', color: 'text-gray-600', desc: 'Iba vysoko isté nálezy. Vynechá 55%+ nálezov.' },
};

const getSensitivity = (conf: number) => {
  if (conf <= 0.02) return SENSITIVITY_INFO.ultra;
  if (conf <= 0.08) return SENSITIVITY_INFO.high;
  if (conf <= 0.20) return SENSITIVITY_INFO.medium;
  return SENSITIVITY_INFO.low;
};

export default function Controls({
  confidence,
  onChangeConfidence,
  viewMode,
  onChangeViewMode,
  imageMode,
  onChangeImageMode,
  colormap,
  onChangeColormap,
}: Props) {
  return (
    <div className="p-4 space-y-4 border-b border-gray-800">
      {/* View Mode Toggle */}
      <div>
        <label className="block text-xs font-semibold text-gray-400 mb-2">
          Zobrazenie
        </label>
        <div className="flex rounded-lg overflow-hidden border border-gray-700">
          <button
            onClick={() => onChangeViewMode("clinical")}
            className={`flex-1 px-3 py-1.5 text-xs font-medium transition-colors ${
              viewMode === "clinical"
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700"
            }`}
          >
            Klinický režim
          </button>
          <button
            onClick={() => onChangeViewMode("patient")}
            className={`flex-1 px-3 py-1.5 text-xs font-medium transition-colors ${
              viewMode === "patient"
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700"
            }`}
          >
            Pacientský režim
          </button>
        </div>
      </div>

      {/* Image Mode Toggle */}
      <div>
        <label className="block text-xs font-semibold text-gray-400 mb-2">
          Režim obrazu
        </label>
        <div className="grid grid-cols-2 gap-1">
          {IMAGE_MODES.map((m) => (
            <button
              key={m.key}
              onClick={() => onChangeImageMode(m.key)}
              className={`px-2 py-1.5 text-[11px] font-medium rounded transition-colors ${
                imageMode === m.key
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* Colormap selector (only when pseudocolor) */}
      {imageMode === "pseudocolor" && (
        <div>
          <label className="block text-xs font-semibold text-gray-400 mb-2">
            Colormap
          </label>
          <div className="grid grid-cols-2 gap-1">
            {COLORMAPS.map((cm) => (
              <button
                key={cm.key}
                onClick={() => onChangeColormap?.(cm.key)}
                className={`px-2 py-1.5 text-[11px] font-medium rounded transition-colors ${
                  colormap === cm.key
                    ? "bg-purple-600 text-white"
                    : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                }`}
              >
                {cm.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Confidence slider (hidden in patient mode) */}
      {viewMode === "clinical" && (
        <div>
          <label className="block text-xs font-semibold text-gray-400 mb-2">
            Prah spoľahlivosti
          </label>
          <input
            type="range"
            min={0.01}
            max={0.95}
            step={0.01}
            value={confidence}
            onChange={(e) => onChangeConfidence(parseFloat(e.target.value))}
            className="w-full accent-blue-500"
          />
          <div className="mt-1 flex justify-between text-[10px] text-gray-500">
            <span>0.01 (Ultra)</span>
            <span>0.05 ★</span>
            <span>0.25</span>
            <span>0.95 (Iba isté)</span>
          </div>
          {(() => {
            const info = getSensitivity(confidence);
            return (
              <p className={`mt-2 rounded bg-gray-800 p-2 text-[11px] ${info.color}`}>
                💡 <strong>{info.label}</strong> — {info.desc}
              </p>
            );
          })()}
        </div>
      )}
    </div>
  );
}
