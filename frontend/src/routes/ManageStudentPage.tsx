import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Button } from "../components/Button";
import { ErrorNote, Loading } from "../components/StateMessage";
import { enrollStudent, fetchStudent, unenrollStudent } from "../features/manage/api";
import { ProjectStatusTag } from "../features/projects/ProjectStatusTag";
import { KIND_LABEL } from "../features/projects/utils";
import { formatDuration } from "../lib/format";

export function ManageStudentPage() {
  const { userId } = useParams();
  const queryClient = useQueryClient();
  const detail = useQuery({
    queryKey: ["manage", "student", userId],
    queryFn: ({ signal }) => fetchStudent(userId as string, signal),
    enabled: Boolean(userId),
  });
  const change = useMutation({
    mutationFn: async ({ slug, enroll }: { slug: string; enroll: boolean }): Promise<void> => {
      if (enroll) await enrollStudent(userId as string, slug);
      else await unenrollStudent(userId as string, slug);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["manage"] }),
  });

  if (detail.isPending) return <Loading label="Loading student" />;
  if (detail.isError) return <ErrorNote error={detail.error} />;
  const data = detail.data;
  const stats: [string, string][] = [
    ["Role", data.user.role],
    ["Lessons done", String(data.lessons_completed)],
    ["Time in lessons", formatDuration(data.time_spent_seconds)],
    ["Exercise attempts", String(data.exercise_attempts)],
    ["Exercises passed", String(data.exercises_passed)],
    ["Last sign-in", data.user.last_login_at ? new Date(data.user.last_login_at).toLocaleString() : "never"],
  ];

  return (
    <div>
      <nav aria-label="Breadcrumb" className="font-mono text-xs text-ink-muted">
        <Link to="/manage/students" className="hover:text-ink">Students</Link> / {data.user.profile.display_name}
      </nav>
      <h1 className="mt-3 font-serif text-3xl">{data.user.profile.display_name}</h1>
      <p className="font-mono text-sm text-ink-muted">
        {data.user.email}. Experience: {data.user.profile.experience_level}.{data.user.is_active ? "" : " Deactivated."}
      </p>

      <dl className="mt-6 grid max-w-3xl gap-x-10 border-y border-rule font-mono text-sm sm:grid-cols-2">
        {stats.map(([label, value]) => (
          <div key={label} className="grid grid-cols-[1fr_auto] gap-3 py-2">
            <dt className="text-ink-muted">{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>

      <section className="mt-10" aria-labelledby="courses-heading">
        <h2 id="courses-heading" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Courses and enrollment</h2>
        <ul className="mt-2 max-w-3xl divide-y divide-rule border-y border-rule text-sm">
          {data.courses.map((course) => (
            <li key={course.id} className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 py-2">
              <span>
                {course.title}
                <span className="block font-mono text-xs text-ink-muted">
                  {course.completed_lesson_count}/{course.published_lesson_count} written lessons done
                </span>
              </span>
              <Button
                variant={course.enrolled ? "danger" : "secondary"}
                disabled={change.isPending}
                onClick={() => change.mutate({ slug: course.slug, enroll: !course.enrolled })}
              >
                {course.enrolled ? "Remove" : "Enroll"}
              </Button>
            </li>
          ))}
        </ul>
        <p className="mt-1 text-xs text-ink-muted">Removing an enrollment keeps the learner's progress.</p>
        {change.isError && <ErrorNote error={change.error} />}
      </section>

      <section className="mt-10" aria-labelledby="projects-heading">
        <h2 id="projects-heading" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Projects</h2>
        <ul className="mt-2 max-w-3xl divide-y divide-rule border-y border-rule text-sm">
          {data.projects.map((project) => (
            <li key={project.id} className="grid grid-cols-[minmax(0,1fr)_auto] gap-3 py-2">
              <span>{project.title} <span className="font-mono text-xs text-ink-muted">({KIND_LABEL[project.kind]})</span></span>
              <ProjectStatusTag status={project.status} />
            </li>
          ))}
        </ul>
        {data.projects.length === 0 && <p className="mt-2 text-sm text-ink-muted">No projects published.</p>}
      </section>

      <section className="mt-10" aria-labelledby="mastery-heading">
        <h2 id="mastery-heading" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Exercise results by concept</h2>
        {data.mastery.length === 0 ? (
          <p className="mt-2 text-sm text-ink-muted">No graded exercises yet.</p>
        ) : (
          <ul className="mt-2 max-w-3xl divide-y divide-rule border-y border-rule text-sm">
            {data.mastery.map((item) => (
              <li key={item.slug} className="grid grid-cols-[minmax(0,1fr)_auto] gap-3 py-2">
                <span>{item.name}</span>
                <span className={`font-mono ${item.correct / item.total < 0.7 ? "text-warn" : "text-ok"}`}>{item.correct}/{item.total}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
