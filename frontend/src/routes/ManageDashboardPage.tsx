import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { ErrorNote, Loading } from "../components/StateMessage";
import { useAuth } from "../features/auth/AuthContext";
import { fetchOverview } from "../features/manage/api";
import { passRate } from "../features/manage/utils";

export function ManageDashboardPage() {
  const { user } = useAuth();
  const overview = useQuery({ queryKey: ["manage", "overview"], queryFn: ({ signal }) => fetchOverview(signal) });
  if (overview.isPending) return <Loading label="Loading dashboard" />;
  if (overview.isError) return <ErrorNote error={overview.error} />;
  const data = overview.data;
  const isAdmin = user?.role === "admin";

  const stats: [string, string][] = [
    ["Students", String(data.users_by_role.student ?? 0)],
    ["Instructors", String(data.users_by_role.instructor ?? 0)],
    ["Admins", String(data.users_by_role.admin ?? 0)],
    ["Active, last 7 days", String(data.active_learners_7d)],
    ["Reviews waiting", String(data.pending_reviews)],
    ["AI requests today", String(data.ai.requests_today)],
    ["AI requests, 7 days", String(data.ai.requests_7d)],
    ["AI tokens, 7 days", data.ai.tokens_7d.toLocaleString()],
  ];

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">{isAdmin ? "Administrator" : "Instructor"}</p>
      <h1 className="mt-2 font-serif text-3xl">{isAdmin ? "Administrator dashboard" : "Instructor dashboard"}</h1>
      <nav aria-label="Manage" className="mt-3 flex flex-wrap gap-5 text-sm">
        <Link to="/manage/students" className="text-signal underline underline-offset-4">Students</Link>
        <Link to="/manage/content" className="text-signal underline underline-offset-4">Content</Link>
        <Link to="/reviews" className="text-signal underline underline-offset-4">Review queue ({data.pending_reviews})</Link>
        {isAdmin && <Link to="/admin/users" className="text-signal underline underline-offset-4">Roles and accounts</Link>}
      </nav>

      <dl className="mt-8 grid gap-x-10 border-y border-rule font-mono text-sm sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(([label, value]) => (
          <div key={label} className="grid grid-cols-[1fr_auto] gap-3 border-rule py-2 sm:border-b">
            <dt className="text-ink-muted">{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>

      <div className="mt-10 grid gap-10 lg:grid-cols-2">
        <section aria-labelledby="enrollments-heading">
          <h2 id="enrollments-heading" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Enrollments by course</h2>
          <ul className="mt-2 divide-y divide-rule border-y border-rule text-sm">
            {data.enrollments.map((item) => (
              <li key={item.course_slug} className="grid grid-cols-[1fr_auto] gap-3 py-2">
                <span>{item.course_title}</span>
                <span className="font-mono">{item.enrolled}</span>
              </li>
            ))}
          </ul>
        </section>

        <section aria-labelledby="top-heading">
          <h2 id="top-heading" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Most completed lessons</h2>
          {data.top_lessons.length === 0 ? (
            <p className="mt-2 text-sm text-ink-muted">No lessons have been completed yet.</p>
          ) : (
            <ul className="mt-2 divide-y divide-rule border-y border-rule text-sm">
              {data.top_lessons.map((item) => (
                <li key={`${item.module_slug}/${item.lesson_slug}`} className="grid grid-cols-[1fr_auto] gap-3 py-2">
                  <Link to={`/courses/${item.course_slug}/${item.module_slug}/${item.lesson_slug}`} className="hover:text-signal">
                    {item.title}
                  </Link>
                  <span className="font-mono">{item.completed}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <section className="mt-10" aria-labelledby="exercise-heading">
        <h2 id="exercise-heading" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Exercise results</h2>
        <p className="mt-1 text-sm text-ink-muted">A learner counts as passed once any attempt passed. Code scores are self-reported.</p>
        {data.exercises.length === 0 ? (
          <p className="mt-2 text-sm text-ink-muted">No exercise attempts yet.</p>
        ) : (
          <div className="mt-2 overflow-x-auto">
            <table className="w-full min-w-[34rem] text-left text-sm">
              <thead className="border-y border-rule font-mono text-xs uppercase tracking-widest text-ink-muted">
                <tr>
                  <th className="py-2 pr-3 font-normal">Exercise</th>
                  <th className="py-2 pr-3 font-normal">Type</th>
                  <th className="py-2 pr-3 font-normal">Attempts</th>
                  <th className="py-2 pr-3 font-normal">Learners</th>
                  <th className="py-2 font-normal">Passed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-rule border-b border-rule">
                {data.exercises.map((item) => (
                  <tr key={item.exercise_id}>
                    <td className="py-2 pr-3">
                      <Link to={`/manage/exercises/${item.exercise_id}`} className="hover:text-signal">{item.title}</Link>
                      <span className="block text-xs text-ink-muted">{item.lesson_title}</span>
                    </td>
                    <td className="py-2 pr-3 font-mono text-xs">{item.kind}</td>
                    <td className="py-2 pr-3 font-mono">{item.attempts}</td>
                    <td className="py-2 pr-3 font-mono">{item.learners}</td>
                    <td className="py-2 font-mono">{passRate(item.passed_learners, item.learners)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
