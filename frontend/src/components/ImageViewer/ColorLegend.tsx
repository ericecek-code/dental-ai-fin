"use client";

type LegendItem = {
  label: string;
  color: string;
  dotted?: boolean;
};

const cariesItems: LegendItem[] = [
  { label: "Skorý kaz (0–30%)", color: "#FFD700" },
  { label: "Stredný kaz (30–60%)", color: "#FF8C00" },
  { label: "Závažný kaz (60–100%)", color: "#FF0000" },
];

const nonCariesItems: LegendItem[] = [
  { label: "Fraktura", color: "#F59E0B" },
  { label: "Implantát", color: "#3B82F6" },
  { label: "Koreň", color: "#8B5CF6" },
];

const viewModeItems: LegendItem[] = [
  { label: "Heatmapa", color: "#FF00FF", dotted: true },
  { label: "Pseudocolor", color: "#00FFFF", dotted: true },
];

type Props = {
  imageMode?: string;
};

export default function ColorLegend({ imageMode }: Props) {
  return (
    <div className="bg-gray-900/80 border border-gray-700/50 rounded-lg px-3 py-2 backdrop-blur-sm flex gap-3 items-center flex-wrap">
      {/* Caries by confidence */}
      <span className="text-[9px] text-gray-500 font-semibold uppercase tracking-wider">
        Kaz:
      </span>
      {cariesItems.map((item) => (
        <div key={item.label} className="flex items-center gap-1.5">
          <span
            className="inline-block w-3 h-3 rounded-sm"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-[10px] text-gray-300">{item.label}</span>
        </div>
      ))}

      <span className="w-px h-3 bg-gray-700" />

      {/* Non-caries */}
      {nonCariesItems.map((item) => (
        <div key={item.label} className="flex items-center gap-1.5">
          <span
            className="inline-block w-3 h-3 rounded-sm"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-[10px] text-gray-300">{item.label}</span>
        </div>
      ))}

      {/* View mode specific items */}
      {imageMode === "heatmap" && (
        <>
          <span className="w-px h-3 bg-gray-700" />
          <div className="flex items-center gap-1.5">
            <span
              className="inline-block w-3 h-3 rounded-sm border border-dashed"
              style={{ borderColor: "#FF00FF" }}
            />
            <span className="text-[10px] text-gray-300">Heatmapa</span>
          </div>
        </>
      )}
      {imageMode === "pseudocolor" && (
        <>
          <span className="w-px h-3 bg-gray-700" />
          <div className="flex items-center gap-1.5">
            <span
              className="inline-block w-3 h-3 rounded-sm border border-dashed"
              style={{ borderColor: "#00FFFF" }}
            />
            <span className="text-[10px] text-gray-300">Pseudocolor</span>
          </div>
        </>
      )}
    </div>
  );
}
