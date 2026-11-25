export type Tick = "done" | "open" | "planned";

export interface TraceCounts {
  published: number;
  completed: number;
  planned: number;
}

function fill(count: number, tick: Tick): Tick[] {
  return Array.from({ length: Math.max(0, count) }, () => tick);
}

/** One tick per lesson: finished, available but unfinished, planned. Long outlines are scaled to `cap` ticks. */
export function buildTicks({ published, completed, planned }: TraceCounts, cap = 40): Tick[] {
  const total = published + planned;
  if (total === 0) return [];
  const done = Math.min(completed, published);
  const open = published - done;
  if (total <= cap) return [...fill(done, "done"), ...fill(open, "open"), ...fill(planned, "planned")];

  const scale = cap / total;
  const scaled = (n: number) => (n > 0 ? Math.max(1, Math.round(n * scale)) : 0);
  return [...fill(scaled(done), "done"), ...fill(scaled(open), "open"), ...fill(scaled(planned), "planned")];
}
