import { useMutation } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button } from "../../components/Button";
import { ErrorNote } from "../../components/StateMessage";
import { LessonMarkdown } from "../curriculum/LessonMarkdown";
import { requestStudyPlan } from "./api";

export function StudyPlanSection() {
  const plan = useMutation({ mutationFn: requestStudyPlan });

  return (
    <section className="mt-10" aria-labelledby="plan-heading">
      <h2 id="plan-heading" className="mb-1 font-mono text-xs uppercase tracking-widest text-ink-muted">
        AI study plan
      </h2>
      <p className="max-w-2xl text-sm text-ink-muted">
        Looks at the concepts you scored below 70% on and writes a short plan. It can only point to lessons and curated
        resources that exist on this platform, and any link it writes itself is removed.
      </p>
      <div className="mt-3">
        <Button onClick={() => plan.mutate()} disabled={plan.isPending}>
          {plan.isPending ? "Writing your plan..." : "Get an AI study plan"}
        </Button>
      </div>
      {plan.isError && (
        <div className="mt-3">
          <ErrorNote error={plan.error} />
        </div>
      )}
      {plan.data && (
        <div className="mt-4 border-t border-rule pt-4">
          <LessonMarkdown source={plan.data.reply} />
          {plan.data.weak_concepts.length > 0 && (
            <ul className="mt-2 divide-y divide-rule border-y border-rule font-mono text-xs">
              {plan.data.weak_concepts.map((item) => (
                <li key={item.slug} className="grid grid-cols-[minmax(0,1fr)_auto] gap-3 py-1">
                  <span className="font-sans text-sm">{item.name}</span>
                  <span className="text-warn">
                    {item.correct}/{item.total}
                  </span>
                </li>
              ))}
            </ul>
          )}
          {plan.data.recommendations.length > 0 && (
            <ol className="mt-4 space-y-1 text-sm">
              {plan.data.recommendations.map((item, index) => (
                <li key={`${item.type}-${item.url ?? item.lesson_slug}-${index}`} className="grid grid-cols-[2.5rem_1fr] gap-1">
                  <span className="font-mono text-xs text-ink-muted">[{index + 1}]</span>
                  <span>
                    {item.type === "lesson" ? (
                      <Link
                        to={`/courses/${item.course_slug}/${item.module_slug}/${item.lesson_slug}`}
                        className="text-signal underline underline-offset-4"
                      >
                        {item.title}
                      </Link>
                    ) : (
                      <a
                        href={item.url ?? undefined}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-signal underline underline-offset-4"
                      >
                        {item.title}
                      </a>
                    )}{" "}
                    <span className="text-ink-muted">
                      {item.type === "lesson" ? "lesson" : item.resource_kind}, for {item.concept_name}
                    </span>
                  </span>
                </li>
              ))}
            </ol>
          )}
        </div>
      )}
    </section>
  );
}
