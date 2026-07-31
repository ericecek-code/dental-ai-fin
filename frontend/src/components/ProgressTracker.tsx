type Props = {
  step?: string;
};

const STATUS_CONFIG: Record<string, { text: string; color: string; icon: string }> = {
  idle: { text: 'Čaká na súbor', color: 'text-dental-textMuted', icon: '⏳' },
  queued: { text: 'Zaradené do fronty', color: 'text-status-boneLoss', icon: '📋' },
  uploading: { text: 'Nahrávanie…', color: 'text-status-lesion', icon: '📤' },
  preprocessing: { text: 'Predspracovanie obrazu', color: 'text-dental-accent', icon: '⚙️' },
  detection: { text: 'Detekcia nálezov', color: 'text-dental-primary', icon: '🔍' },
  done: { text: 'Dokončené', color: 'text-status-healthy', icon: '✅' },
  error: { text: 'Chyba', color: 'text-status-caries', icon: '❌' },
};

const ProgressTracker = ({ step = 'idle' }: Props) => {
  const config = STATUS_CONFIG[step] || { text: step, color: 'text-dental-textMuted', icon: '•' };

  return (
    <div className="glass-panel px-3 py-2.5 text-[11px] flex items-center gap-2">
      <span>{config.icon}</span>
      <span className="font-semibold text-dental-textMuted">Stav:</span>
      <span className={config.color}>{config.text}</span>
    </div>
  );
};

export default ProgressTracker;
