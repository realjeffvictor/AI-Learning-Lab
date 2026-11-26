import { Link } from "react-router-dom";

import type { SubmissionResult } from "./types";

export function ResultPanel({ result }: { result: SubmissionResult }) {
  const lessons = result.recommendations.filter((item) => item.type === "lesson");
  const resources = result.recommendations.filter((item) => item.type === "resource");
  return (
    <section aria-label="Result" className="mt-4 border-t border-rule pt-4">
      <p className="font-mono text-2xl">
        {result.score}
        <span className="text-base text-ink-muted"> / 100</span>
      </p>
      <p className={result.passed ? "text-ok" : "text-warn"}>
        {result.passed ? "Passed" : `Not passed yet. You need ${result.pass_score}.`} Attempt {result.attempt_number}.
      </p>

      <ul className="mt-3 divide-y divide-rule border-y border-rule font-mono text-xs">
        {result.concept_results.map((item) => (
          <li key={item.slug} className="grid grid-cols-[minmax(0,1fr)_auto] gap-3 py-1">
            <span className="font-sans text-sm">{item.name}</span>
            <span className={item.correct === item.total ? "text-ok" : "text-warn"}>
              {item.correct}/{item.total}
            </span>
          </li>
        ))}
      </ul>

      {result.recommendations.length > 0 && (
        <div className="mt-4 text-sm">
          <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Review these next</p>
          {lessons.length > 0 && (
            <ul className="mt-2 space-y-1">
              {lessons.map((item) => (
                <li key={`${item.concept_slug}-${item.lesson_slug}`}>
                  <Link
                    to={`/courses/${item.course_slug}/${item.module_slug}/${item.lesson_slug}`}
                    className="text-signal underline underline-offset-4"
                  >
                    {item.title}
                  </Link>{" "}
                  <span className="text-ink-muted">on this platform, for {item.concept_name}</span>
                </li>
              ))}
            </ul>
          )}
          {resources.length > 0 && (
            <ul className="mt-2 space-y-1">
              {resources.map((item) => (
                <li key={item.url}>
                  <a
                    href={item.url ?? undefined}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-signal underline underline-offset-4"
                  >
                    {item.title}
                  </a>{" "}
                  <span className="text-ink-muted">
                    {item.resource_kind}
                    {item.is_open_source ? ", open" : ""}, for {item.concept_name}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </section>
  );
}
