"use client";

import { useCallback, useState, useRef, useImperativeHandle, forwardRef } from 'react';

type Props = {
  onFile: (file: File) => void;
};

type UploadZoneHandle = {
  openFilePicker: () => void;
};

const ACCEPTED_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/tiff", "image/dicom", "application/dicom"];
const MAX_SIZE_MB = 50;

const UploadZone = forwardRef<UploadZoneHandle, Props>(({ onFile }, ref) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useImperativeHandle(ref, () => ({
    openFilePicker: () => {
      inputRef.current?.click();
    },
  }));

  const dispatchToast = useCallback((type: "success" | "error" | "warning" | "info", message: string) => {
    window.dispatchEvent(
      new CustomEvent("dental-toast", { detail: { type, message } }),
    );
  }, []);

  const validateAndProcess = useCallback((file: File) => {
    // Type check
    if (!ACCEPTED_TYPES.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png|tif|tiff|dcm)$/i)) {
      dispatchToast("error", "Neplatný typ súboru");
      return;
    }

    // Size check
    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > MAX_SIZE_MB) {
      dispatchToast("error", `Súbor je príliš veľký (max ${MAX_SIZE_MB} MB)`);
      return;
    }

    setFile(file);
    onFile(file);
  }, [onFile, dispatchToast]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragActive(false);
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) validateAndProcess(droppedFile);
    },
    [validateAndProcess],
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragActive(false);
  }, []);

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0];
      if (selectedFile) validateAndProcess(selectedFile);
      e.target.value = ""; // reset so same file can be selected again
    },
    [validateAndProcess],
  );

  const removeFile = () => {
    setFile(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const openFilePicker = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const hasFile = file !== null;

  return (
    <div
      className={`drop-zone ${isDragActive ? "drag-active" : ""}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={openFilePicker}
      role="button"
      tabIndex={0}
      aria-label="Nahrať RTG snímku"
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openFilePicker();
        }
      }}
    >
      {hasFile ? (
        <div className="flex flex-col items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 border border-emerald-500/30">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#10B981"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
          <div className="text-center">
            <h3 className="text-sm font-semibold text-slate-100">Súbor vybratý</h3>
            <p className="text-xs text-slate-400 truncate max-w-xs">{file.name}</p>
            <p className="text-xs text-slate-500 mt-0.5">
              {(file.size / 1024 / 1024).toFixed(2)} MB • {file.type}
            </p>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              removeFile();
            }}
            className="mt-2 text-xs text-slate-400 hover:text-red-400 transition-colors"
          >
            Odstrániť
          </button>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center gap-3">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-cyan-500/10 border border-cyan-500/30 group-hover:bg-cyan-500/20 transition-colors">
            <svg
              width="26"
              height="26"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#0EA5E9"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <h3 className="text-sm font-semibold text-slate-200">Nahrajte panoramatický RTG</h3>
          <p className="text-xs text-slate-500">
            Kliknite alebo ťahajte sem snímku
          </p>
          <p className="text-[10px] text-slate-600 mt-0.5">
            JPEG, PNG, TIFF, DICOM • max {MAX_SIZE_MB} MB
          </p>
        </div>
      )}

      {/* Input musí byť v DOM vždy — inak klik po výbere súboru nič neurobí */}
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept="image/*,.dcm"
        onChange={handleFileSelect}
      />
    </div>
  );
});

UploadZone.displayName = "UploadZone";

export default UploadZone;