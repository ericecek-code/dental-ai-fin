import { useCallback } from 'react';

type Props = {
  onFile: (file: File) => void;
};

const UploadZone = ({ onFile }: Props) => {
  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onFile(file);
    },
    [onFile],
  );

  return (
    <label className="glass-panel flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-dental-surfaceHighlight hover:border-dental-primary/50 p-6 transition-all duration-300 group scan-line-overlay">
      <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-dental-primary/10 group-hover:bg-dental-primary/20 transition-colors">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#0D9488"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
      </div>
      <span className="text-sm font-medium text-dental-textMain">
        Kliknite pre nahratie RTG snímky
      </span>
      <span className="mt-1 text-[10px] text-dental-textMuted">
        JPEG, PNG, DICOM • max 20 MB
      </span>
      <input type="file" className="hidden" accept="image/*" onChange={onChange} />
    </label>
  );
};

export default UploadZone;
