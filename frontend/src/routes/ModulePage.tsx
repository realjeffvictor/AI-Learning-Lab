import { Link, useParams } from "react-router-dom";

import { ErrorNote, Loading } from "../components/StateMessage";
import { useCourse } from "../features/curriculum/hooks";
import { LessonRow } from "../features/curriculum/LessonRow";
import { StatusTag } from "../features/curriculum/StatusTag";

export function ModulePage() {
  const { courseSlug, moduleSlug } = useParams();
  const course = useCourse(courseSlug);

  if (course.isPending) return <Loading label="Loading module" />;
  if (course.isError) return <ErrorNote error={course.error} />;

  const module = course.data.modules.find((item) => item.slug === moduleSlug);
  if (!module) {
    return (
      <div>
        <p className="font-mono text-sm text-ink-muted">404</p>
        <h1 className="mt-2 font-serif text-3xl">Module not found</h1>
        <Link to={`/courses/${course.data.slug}`} className="mt-4 inline-block text-signal underline underline-offset-4">
          Back to {course.data.title}
        </Link>
      </div>
    );
  }

  return (
    <div>
      <nav aria-label="Breadcrumb" className="font-mono text-xs text-ink-muted">
        <Link to="/courses" className="hover:text-ink">
          Curriculum
        </Link>{" "}
        /{" "}
        <Link to={`/courses/${course.data.slug}`} className="hover:text-ink">
          {course.data.title}
        </Link>{" "}
        / {module.title}
      </nav>
      <div className="mt-3 flex flex-wrap items-baseline gap-4">
        <h1 className="font-serif text-3xl">{module.title}</h1>
        <StatusTag status={module.status} />
      </div>
      {module.summary && <p className="mt-2 max-w-2xl text-ink-muted">{module.summary}</p>}

      {module.lessons.length > 0 ? (
        <ul className="mt-8 max-w-3xl divide-y divide-rule border-y border-rule">
          {module.lessons.map((lesson, index) => (
            <LessonRow
              key={lesson.id}
              courseSlug={course.data.slug}
              moduleSlug={module.slug}
              lesson={lesson}
              index={index}
              showSummary
            />
          ))}
        </ul>
      ) : (
        <p className="mt-8 text-ink-muted">This module is in the outline but has no lessons written yet.</p>
      )}
    </div>
  );
}
