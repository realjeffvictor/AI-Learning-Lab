import { Link } from "react-router-dom";

import { ErrorNote, Loading } from "../components/StateMessage";
import { useAuth } from "../features/auth/AuthContext";
import { useProgressSummary } from "../features/curriculum/hooks";
import { ProgressTrace } from "../features/curriculum/ProgressTrace";
import { formatDuration } from "../lib/format";

export function DashboardPage() {
  const { user } = useAuth();
  const summary = useProgressSummary();
  if (!user) return null;

  const upNext = summary.data?.up_next ?? null;
  const enrolled = summary.data?.courses.filter((course) => course.enrolled) ?? [];

  return (
    <div className="grid gap-12 lg:grid-cols-[minmax(0,1fr)_22rem]">
      <section>
        <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Dashboard</p>
        <h1 className="mt-2 font-serif text-3xl">Welcome, {user.profile.display_name}</h1>

        {summary.isPending && <div className="mt-6"><Loading label="Loading your progress" /></div>}
        {summary.isError && <div className="mt-6"><ErrorNote error={summary.error} /></div>}

        {summary.data && (
          <>
            <div className="mt-8 border-y border-rule py-5">
              {upNext ? (
                <>
                  <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">
                    {upNext.reason === "continue" ? "Continue where you left off" : "Start here"}
                  </p>
                  <p className="mt-1 font-serif text-2xl">{upNext.lesson_title}</p>
                  <p className="text-sm text-ink-muted">{upNext.course_title}</p>
                  <Link
                    to={`/courses/${upNext.course_slug}/${upNext.module_slug}/${upNext.lesson_slug}`}
                    className="mt-3 inline-block rounded-md bg-signal px-3 py-1.5 text-sm font-medium text-signal-ink"
                  >
                    {upNext.reason === "continue" ? "Continue lesson" : "Start lesson"}
                  </Link>
                </>
              ) : (
                <>
                  <p className="font-serif text-xl">You have finished every lesson written so far.</p>
                  <p className="mt-1 text-sm text-ink-muted">
                    More lessons are in the outline as Planned. Browse the curriculum to see what is coming.
                  </p>
                  <Link to="/courses" className="mt-3 inline-block text-signal underline underline-offset-4">
                    Open curriculum
                  </Link>
                </>
              )}
            </div>

            <h2 className="mb-2 mt-10 font-mono text-xs uppercase tracking-widest text-ink-muted">My courses</h2>
            {enrolled.length === 0 ? (
              <p className="text-sm text-ink-muted">
                You are not enrolled in anything yet. Starting a lesson enrolls you in its course automatically.
              </p>
            ) : (
              <ul className="divide-y divide-rule border-y border-rule">
                {enrolled.map((course) => (
                  <li key={course.id} className="grid gap-2 py-3 sm:grid-cols-[minmax(0,1fr)_16rem]">
                    <Link to={`/courses/${course.slug}`} className="font-serif text-lg hover:text-signal">
                      {course.title}
                    </Link>
                    <ProgressTrace
                      published={course.published_lesson_count}
                      completed={course.completed_lesson_count}
                      planned={course.planned_lesson_count}
                    />
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </section>

      <section aria-labelledby="stats-heading">
        <h2 id="stats-heading" className="mb-3 font-mono text-xs uppercase tracking-widest text-ink-muted">
          At a glance
        </h2>
        <dl className="divide-y divide-rule border-y border-rule font-mono text-sm">
          {[
            ["Lessons done", summary.data ? String(summary.data.lessons_completed) : "none"],
            ["Time learning", summary.data ? formatDuration(summary.data.time_spent_seconds) : "none"],
            ["Role", user.role],
            ["Experience", user.profile.experience_level],
          ].map(([label, value]) => (
            <div key={label} className="grid grid-cols-[8rem_1fr] gap-2 py-2">
              <dt className="text-ink-muted">{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
        <Link to="/progress" className="mt-4 inline-block text-sm text-signal underline underline-offset-4">
          Full progress and competencies
        </Link>
      </section>
    </div>
  );
}
