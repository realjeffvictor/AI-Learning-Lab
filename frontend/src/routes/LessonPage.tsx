import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { Link, useParams } from "react-router-dom";

import { Button } from "../components/Button";
import { ErrorNote, Loading } from "../components/StateMessage";
import { completeLesson, startLesson } from "../features/curriculum/api";
import { invalidateProgressQueries, useCourse, useLesson } from "../features/curriculum/hooks";
import { LessonMarkdown } from "../features/curriculum/LessonMarkdown";
import { PrincipleGlyphs } from "../features/curriculum/PrincipleGlyphs";
import type { CourseDetail } from "../features/curriculum/types";
import { useLessonTimer } from "../features/curriculum/useLessonTimer";
import { formatDuration } from "../lib/format";

function Outline({ course, currentSlug, moduleSlug }: { course: CourseDetail; currentSlug: string; moduleSlug: string }) {
  return (
    <nav aria-label="Course outline" className="text-sm">
      <p className="mb-2 font-mono text-xs uppercase tracking-widest text-ink-muted">Outline</p>
      <ol className="space-y-3">
        {course.modules.map((module) => (
          <li key={module.id}>
            <p className="text-ink-muted">{module.title}</p>
            <ul className="mt-1 border-l border-rule pl-3">
              {module.lessons.map((lesson) => {
                const current = module.slug === moduleSlug && lesson.slug === currentSlug;
                const marker = lesson.progress === "completed" ? "done" : lesson.progress === "in_progress" ? "in progress" : "";
                return (
                  <li key={lesson.id} className="py-0.5">
                    {lesson.status === "published" ? (
                      <Link
                        to={`/courses/${course.slug}/${module.slug}/${lesson.slug}`}
                        aria-current={current ? "page" : undefined}
                        className={current ? "text-signal" : "hover:text-signal"}
                      >
                        {lesson.title}
                      </Link>
                    ) : (
                      <span className="text-ink-muted">{lesson.title} (planned)</span>
                    )}
                    {marker && <span className="ml-2 font-mono text-xs text-ink-muted">{marker}</span>}
                  </li>
                );
              })}
            </ul>
          </li>
        ))}
      </ol>
    </nav>
  );
}

export function LessonPage() {
  const { courseSlug, moduleSlug, lessonSlug } = useParams();
  const lesson = useLesson(courseSlug, moduleSlug, lessonSlug);
  const course = useCourse(courseSlug);
  const queryClient = useQueryClient();

  const lessonId = lesson.data && lesson.data.status === "published" ? lesson.data.id : null;

  const start = useMutation({
    mutationFn: (id: string) => startLesson(id),
    onSuccess: () => invalidateProgressQueries(queryClient),
  });
  const startedFor = useRef<string | null>(null);
  useEffect(() => {
    if (!lessonId || startedFor.current === lessonId) return;
    startedFor.current = lessonId;
    start.mutate(lessonId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lessonId]);

  useLessonTimer(lessonId, start.isSuccess);

  const complete = useMutation({
    mutationFn: () => completeLesson(lessonId as string),
    onSuccess: () => invalidateProgressQueries(queryClient),
  });

  if (lesson.isPending) return <Loading label="Loading lesson" />;
  if (lesson.isError) return <ErrorNote error={lesson.error} />;
  const data = lesson.data;
  const completed = data.progress.status === "completed";

  return (
    <div className="grid gap-10 lg:grid-cols-[13rem_minmax(0,1fr)_17rem]">
      <aside className="hidden lg:block">
        {course.data && <Outline course={course.data} currentSlug={data.slug} moduleSlug={data.module_slug} />}
      </aside>

      <article>
        <nav aria-label="Breadcrumb" className="font-mono text-xs text-ink-muted">
          <Link to="/courses" className="hover:text-ink">
            Curriculum
          </Link>{" "}
          /{" "}
          <Link to={`/courses/${data.course_slug}`} className="hover:text-ink">
            {data.course_title}
          </Link>{" "}
          /{" "}
          <Link to={`/courses/${data.course_slug}/${data.module_slug}`} className="hover:text-ink">
            {data.module_title}
          </Link>
        </nav>
        <h1 className="mt-3 font-serif text-4xl leading-tight">{data.title}</h1>
        {data.summary && <p className="mt-2 max-w-2xl font-serif text-lg text-ink-muted">{data.summary}</p>}

        <div className="mt-8">
          {data.content_md ? (
            <LessonMarkdown source={data.content_md} />
          ) : (
            <p className="max-w-xl border border-dashed border-ink-muted p-4 text-ink-muted">
              This lesson is planned and has not been written yet. It is in the outline so you can see where the course
              is going.
            </p>
          )}
        </div>

        <div className="mt-12 flex flex-wrap justify-between gap-4 border-t border-rule pt-4 text-sm">
          {data.previous ? (
            <Link
              to={`/courses/${data.course_slug}/${data.previous.module_slug}/${data.previous.slug}`}
              className="hover:text-signal"
            >
              Previous: {data.previous.title}
            </Link>
          ) : (
            <span />
          )}
          {data.next && (
            <Link
              to={`/courses/${data.course_slug}/${data.next.module_slug}/${data.next.slug}`}
              className="hover:text-signal"
            >
              Next: {data.next.title}
            </Link>
          )}
        </div>
      </article>

      <aside className="space-y-6 text-sm">
        {lessonId && (
          <section aria-label="Lesson status">
            <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Status</p>
            {completed ? (
              <p className="mt-2 text-ok">Completed</p>
            ) : (
              <>
                <p className="mt-2 text-ink-muted">{data.progress.status === "in_progress" ? "In progress" : "Not started"}</p>
                <Button className="mt-3" onClick={() => complete.mutate()} disabled={complete.isPending || !start.isSuccess}>
                  {complete.isPending ? "Saving..." : "Mark lesson complete"}
                </Button>
                {complete.isError && <ErrorNote error={complete.error} />}
              </>
            )}
            <p className="mt-3 font-mono text-xs text-ink-muted">
              About {data.estimated_minutes} min. Time here: {formatDuration(data.progress.time_spent_seconds)}
            </p>
          </section>
        )}

        {data.objectives.length > 0 && (
          <section aria-label="Learning objectives">
            <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">You will be able to</p>
            <ul className="mt-2 list-disc space-y-1 pl-4">
              {data.objectives.map((objective) => (
                <li key={objective}>{objective}</li>
              ))}
            </ul>
          </section>
        )}

        {data.principles.length > 0 && (
          <section aria-label="Principles">
            <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Principles practised</p>
            <p className="mt-2">
              <PrincipleGlyphs principles={data.principles} />
            </p>
          </section>
        )}

        {data.concepts.length > 0 && (
          <section aria-label="Concepts">
            <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Concepts</p>
            <ul className="mt-2 space-y-1">
              {data.concepts.map((concept) => (
                <li key={concept.slug} className="grid grid-cols-[1.25rem_1fr] gap-1">
                  <span className="font-mono text-xs text-ink-muted" title={`Category ${concept.category}`}>
                    {concept.category}
                  </span>
                  <span>{concept.name}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </aside>
    </div>
  );
}
