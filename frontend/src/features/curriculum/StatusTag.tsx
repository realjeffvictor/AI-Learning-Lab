import type { LessonStatus } from "./types";

export function StatusTag({ status }: { status: LessonStatus }) {
  return status === "published" ? (
    <span className="font-mono text-xs uppercase tracking-widest text-ok">Available</span>
  ) : (
    <span className="border border-dashed border-ink-muted px-1.5 font-mono text-xs uppercase tracking-widest text-ink-muted">
      Planned
    </span>
  );
}
