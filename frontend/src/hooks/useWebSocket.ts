export function useWebSocket(jobId: string | null) {
  if (!jobId) return { status: 'idle' as const };

  if (typeof window === 'undefined') {
    return { status: 'idle' as const };
  }

  return new WebSocket(`ws://127.0.0.1:8000/ws/status/${jobId}`);
}
