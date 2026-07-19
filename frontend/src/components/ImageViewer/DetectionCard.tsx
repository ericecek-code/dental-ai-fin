import { translateClass } from '../../lib/labels';

type Detection = {
  label: string;
  raw_label?: string;
  confidence: number;
  bbox: number[];
  tooth_number?: string;
};

type Props = {
  detections: Detection[];
};

const DetectionCard = ({ detections }: Props) => {
  return (
    <div className="rounded-md border bg-white p-3">
      <h3 className="mb-2 text-sm font-semibold">Nájdené nálezy</h3>
      <div className="space-y-2 text-xs">
        {detections.length === 0 && <p className="text-gray-500">Žiadne nálezy</p>}
        {detections.map((det, idx) => {
          const sk = translateClass(det.label);
          const tooth = det.tooth_number && det.tooth_number !== '?' ? det.tooth_number : null;
          return (
            <div key={idx} className="flex items-start justify-between gap-2 rounded-md border p-2">
              <div className="min-w-0 flex-1">
                <div className="font-medium">
                  {sk}
                  {sk !== det.label && (
                    <span className="ml-1 text-[10px] text-gray-400">
                      ({det.label})
                    </span>
                  )}
                </div>
                <div className="text-gray-600">
                  Pravdepodobnosť: {(det.confidence * 100).toFixed(1)}%
                </div>
              </div>
              <div className="shrink-0 rounded bg-blue-50 px-2 py-1 text-[11px] font-mono font-semibold text-blue-700">
                {tooth ? `Zub ${tooth}` : 'Zub ?'}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default DetectionCard;
