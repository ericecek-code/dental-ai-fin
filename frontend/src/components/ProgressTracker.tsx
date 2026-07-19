type Props = {
  step?: string;
};

const ProgressTracker = ({ step = 'idle' }: Props) => {
  const statusText = {
    idle: 'Čaká na súbor',
    queued: 'Zaradené do fronty',
    uploading: 'Nahrávanie…',
    preprocessing: 'Predspracovanie obrazu',
    detection: 'Detekcia nálezov',
    done: 'Dokončené',
    error: 'Chyba',
  }[step] || step;

  return (
    <div className="rounded-md border bg-white p-3 text-xs">
      <span className="font-semibold">Stav: </span>
      <span className="ml-1 text-gray-700">{statusText}</span>
    </div>
  );
};

export default ProgressTracker;
