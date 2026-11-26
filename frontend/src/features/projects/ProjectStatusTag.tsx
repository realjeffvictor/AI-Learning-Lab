import type { ProjectStatus } from "./types";
import { STATUS_LABEL } from "./utils";

const TONE: Record<ProjectStatus, string> = {
  not_started: "text-ink-muted",
  draft: "text-signal",
  submitted: "text-info",
  approved: "text-ok",
  changes_requested: "text-warn",
};

export function ProjectStatusTag({ status }: { status: ProjectStatus }) {
  return <span className={`font-mono text-xs uppercase tracking-widest ${TONE[status]}`}>{STATUS_LABEL[status]}</span>;
}
