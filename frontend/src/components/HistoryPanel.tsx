import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_BASE = window.location.origin;

type Analysis = {
  id: string;
  created_at: string;
  filename: string;
  detection_count: number;
  health_score: number;
};

type Props = {
  onSelectJob?: (jobId: string) => void;
};

export default function HistoryPanel({ onSelectJob }: Props) {
  const { data: history, isLoading } = useQuery({
    queryKey: ['history'],
    queryFn: () => axios.get(`${API_BASE}/history`).then((r) => r.data),
    staleTime: 30000,
  });

  if (!history?.length) {
    return (
      <div className="glass-panel rounded-2xl p-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
          Posledné analýzy
        </h3>
        <p className="text-[11px] text-dental-textMuted text-center py-3">
          {isLoading ? 'Načítavam...' : 'Žiadne predchádzajúce analýzy'}
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl p-4">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-dental-textMuted mb-3">
        Posledné analýzy
      </h3>
      <div className="space-y-2">
        {history.slice(0, 5).map((item: Analysis) => (
          <div
            key={item.id}
            onClick={() => onSelectJob?.(item.id)}
            className="flex items-center justify-between p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-800 cursor-pointer transition-colors group"
          >
            <div className="min-w-0 flex-1">
              <p className="text-[11px] font-medium text-white truncate group-hover:text-dental-primary transition-colors">
                {item.filename}
              </p>
              <p className="text-[10px] text-dental-textMuted">
                {new Date(item.created_at).toLocaleDateString('sk-SK')}
              </p>
            </div>
            <div className="text-right shrink-0 ml-2">
              <p className="text-[11px] font-semibold text-dental-primary">
                {item.detection_count} nálezov
              </p>
              <p className="text-[10px] text-dental-textMuted">
                {item.health_score != null ? `${item.health_score}%` : '—'}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
