import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Button } from "../components/Button";
import { ErrorNote, Loading } from "../components/StateMessage";
import { enrollInCourse } from "../features/curriculum/api";
import { invalidateProgressQueries, useCourse } from "../features/curriculum/hooks";
import { LessonRow } from "../features/curriculum/LessonRow";
import { ProgressTrace } from "../features/curriculum/ProgressTrace";
import { StatusTag } from "../features/curriculum/StatusTag";

export function CourseDetailPage() {
  const { courseSlug } = useParams();
  const course = useCourse(courseSlug);
  const queryClient = useQueryClient();
  const enroll = useMutation({
    mutationFn: () => enrollInCourse(courseSlug as string),
    onSuccess: () => invalidateProgressQueries(queryClient),
  });

  if (course.isPending) return <Loading label="Loading course" />;
  if (course.isError) return <ErrorNote error={course.error} />;
  const data = course.data;

  return (
    <div>
      <nav aria-label="Breadcrumb" className="font-mono text-xs text-ink-muted">
        <Link to="/courses" className="hover:text-ink">
          Curriculum
        </Link>{" "}
        / {data.title}
      </nav>
      <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">
            {data.kind === "stage" ? `Stage ${data.stage_number}` : "Track"}
          </p>
          <h1 className="mt-1 font-serif text-3xl">{data.title}</h1>
          <p className="mt-2 max-w-2xl text-ink-muted">{data.summary}</p>
        </div>
        <div className="flex flex-col items-start gap-2">
          {data.enrolled ? (
            <span className="font-mono text-xs uppercase tracking-widest text-ok">Enrolled</span>
          ) : (
            <Button onClick={() => enroll.mutate()} disabled={enroll.isPending}>
              {enroll.isPending ? "Enrolling..." : "Enroll in this course"}
            </Button>
          )}
          {enroll.isError && <ErrorNote error={enroll.error} />}
        </div>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-4 font-mono text-xs text-ink-muted">
        <ProgressTrace
          published={data.published_lesson_count}
          completed={data.completed_lesson_count}
          planned={data.planned_lesson_count}
        />
        <span>
          {data.completed_lesson_count}/{data.published_lesson_count} written lessons done
        </span>
      </div>

      <div className="mt-8 divide-y divide-rule border-y border-rule">
        {data.modules.map((module, index) => (
          <section key={module.id} className="py-5">
            <div className="flex flex-wrap items-baseline gap-4">
              <span className="font-mono text-sm text-ink-muted">{String(index + 1).padStart(2, "0")}</span>
              <h2 className="font-serif text-xl">
                <Link to={`/courses/${data.slug}/${module.slug}`} className="hover:text-signal">
                  {module.title}
                </Link>
              </h2>
              <StatusTag status={module.status} />
            </div>
            {module.summary && <p className="mt-1 max-w-2xl pl-10 text-sm text-ink-muted">{module.summary}</p>}
            {module.lessons.length > 0 ? (
              <ul className="mt-2 pl-8">
                {module.lessons.map((lesson, lessonIndex) => (
                  <LessonRow
                    key={lesson.id}
                    courseSlug={data.slug}
                    moduleSlug={module.slug}
                    lesson={lesson}
                    index={lessonIndex}
                  />
                ))}
              </ul>
            ) : (
              <p className="mt-2 pl-10 text-sm text-ink-muted">No lessons written yet.</p>
            )}
          </section>
        ))}
      </div>
    </div>
  );
}
