import { Link } from "react-router-dom";

import { ErrorNote, Loading } from "../components/StateMessage";
import { useCourses } from "../features/curriculum/hooks";
import { ProgressTrace } from "../features/curriculum/ProgressTrace";
import type { CourseSummary } from "../features/curriculum/types";

function countsLabel(course: CourseSummary): string {
  if (course.published_lesson_count === 0) return "No lessons written yet";
  return `${course.completed_lesson_count}/${course.published_lesson_count} done, ${course.planned_lesson_count} planned`;
}

function CourseRow({ course }: { course: CourseSummary }) {
  const label = course.kind === "stage" ? String(course.stage_number).padStart(2, "0") : "TRK";
  return (
    <li className="grid gap-3 py-5 md:grid-cols-[3.5rem_minmax(0,1fr)_16rem] md:gap-6">
      <span className="font-mono text-sm text-ink-muted">{label}</span>
      <div>
        <Link to={`/courses/${course.slug}`} className="font-serif text-xl hover:text-signal">
          {course.title}
        </Link>
        <p className="mt-1 max-w-xl text-sm text-ink-muted">{course.summary}</p>
      </div>
      <div className="flex flex-col gap-2 font-mono text-xs text-ink-muted">
        <ProgressTrace
          published={course.published_lesson_count}
          completed={course.completed_lesson_count}
          planned={course.planned_lesson_count}
        />
        <span>
          {course.module_count} modules. {countsLabel(course)}
        </span>
        {course.enrolled && <span className="text-ok">Enrolled</span>}
      </div>
    </li>
  );
}

export function CoursesPage() {
  const courses = useCourses();
  if (courses.isPending) return <Loading label="Loading curriculum" />;
  if (courses.isError) return <ErrorNote error={courses.error} />;

  const stages = courses.data.filter((course) => course.kind === "stage");
  const tracks = courses.data.filter((course) => course.kind === "track");

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Curriculum</p>
      <h1 className="mt-2 font-serif text-3xl">From Python to intelligent automation</h1>
      <p className="mt-2 max-w-2xl text-ink-muted">
        Five stages in order, with one track that runs alongside all of them. Lessons marked Planned are in the outline
        but have not been written yet.
      </p>

      <h2 className="mb-1 mt-10 font-mono text-xs uppercase tracking-widest text-ink-muted">Stages</h2>
      <ul className="divide-y divide-rule border-y border-rule">
        {stages.map((course) => (
          <CourseRow key={course.id} course={course} />
        ))}
      </ul>

      {tracks.length > 0 && (
        <>
          <h2 className="mb-1 mt-10 font-mono text-xs uppercase tracking-widest text-ink-muted">
            Runs alongside every stage
          </h2>
          <ul className="divide-y divide-rule border-y border-rule">
            {tracks.map((course) => (
              <CourseRow key={course.id} course={course} />
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
