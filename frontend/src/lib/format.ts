export function formatDuration(seconds: number): string {
  if (seconds <= 0) return "none yet";
  if (seconds < 60) return "under 1 min";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  return `${hours} h ${String(minutes % 60).padStart(2, "0")} min`;
}
