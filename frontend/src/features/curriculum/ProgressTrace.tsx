import { buildTicks, type Tick, type TraceCounts } from "./trace";

const TICK_CLASS: Record<Tick, string> = {
  done: "h-3 w-1.5 bg-ok",
  open: "h-3 w-1.5 bg-rule",
  planned: "h-3 w-1.5 border border-dashed border-ink-muted",
};

export function ProgressTrace(counts: TraceCounts) {
  const ticks = buildTicks(counts);
  if (ticks.length === 0) return <span className="font-mono text-xs text-ink-muted">outline only</span>;
  return (
    <div
      role="img"
      aria-label={`${counts.completed} of ${counts.published} written lessons completed, ${counts.planned} planned`}
      className="flex flex-wrap gap-[2px]"
    >
      {ticks.map((tick, index) => (
        <span key={index} className={TICK_CLASS[tick]} />
      ))}
    </div>
  );
}
