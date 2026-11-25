import { Link } from "react-router-dom";

import { PrincipleGlyphs } from "./PrincipleGlyphs";
import { StatusTag } from "./StatusTag";
import type { LessonSummary, ProgressStatus } from "./types";

const PROGRESS_LABEL: Record<ProgressStatus, string> = {
  not_started: "",
  in_progress: "In progress",
  completed: "Completed",
};

interface LessonRowProps {
  courseSlug: string;
  moduleSlug: string;
  lesson: LessonSummary;
  index: number;
  showSummary?: boolean;
}

export function LessonRow({ courseSlug, moduleSlug, lesson, index, showSummary = false }: LessonRowProps) {
  const published = lesson.status === "published";
  const progress = PROGRESS_LABEL[lesson.progress];
  return (
    <li className="grid grid-cols-[2rem_minmax(0,1fr)_auto] items-baseline gap-3 py-2">
      <span className="font-mono text-xs text-ink-muted">{String(index + 1).padStart(2, "0")}</span>
      <div>
        {published ? (
          <Link to={`/courses/${courseSlug}/${moduleSlug}/${lesson.slug}`} className="hover:text-signal">
            {lesson.title}
          </Link>
        ) : (
          <span className="text-ink-muted">{lesson.title}</span>
        )}
        {showSummary && lesson.summary && <p className="mt-1 text-sm text-ink-muted">{lesson.summary}</p>}
      </div>
      <div className="flex items-center gap-3 font-mono text-xs text-ink-muted">
        {published && <PrincipleGlyphs principles={lesson.principles} />}
        {published && <span>{lesson.estimated_minutes} min</span>}
        {progress && <span className={lesson.progress === "completed" ? "text-ok" : "text-signal"}>{progress}</span>}
        <StatusTag status={lesson.status} />
      </div>
    </li>
  );
}
