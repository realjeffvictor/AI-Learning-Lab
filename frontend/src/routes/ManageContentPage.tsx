import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { ErrorNote, Loading } from "../components/StateMessage";
import { fetchContentTree } from "../features/manage/api";
import { KIND_LABEL } from "../features/projects/utils";

export function ManageContentPage() {
  const tree = useQuery({ queryKey: ["manage", "content"], queryFn: ({ signal }) => fetchContentTree(signal) });
  if (tree.isPending) return <Loading label="Loading content" />;
  if (tree.isError) return <ErrorNote error={tree.error} />;

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Manage</p>
      <h1 className="mt-2 font-serif text-3xl">Content</h1>
      <p className="mt-2 max-w-2xl text-ink-muted">
        Lessons, exercises and projects. Anything you change here is marked "edited in app", and re-running the seed
        command will not overwrite it.
      </p>

      <div className="mt-8 space-y-4">
        {tree.data.courses.map((course) => (
          <details key={course.id} className="border-y border-rule py-3">
            <summary className="cursor-pointer font-serif text-xl">
              {course.title}
              <span className="ml-3 font-mono text-xs text-ink-muted">
                {course.modules.length} modules, {course.projects.length} projects
              </span>
            </summary>

            {course.projects.length > 0 && (
              <ul className="mt-3 divide-y divide-rule border-y border-rule text-sm">
                {course.projects.map((project) => (
                  <li key={project.id} className="grid grid-cols-[minmax(0,1fr)_auto] gap-3 py-2">
                    <Link to={`/manage/projects/${project.id}`} className="hover:text-signal">
                      {project.title} <span className="font-mono text-xs text-ink-muted">({KIND_LABEL[project.kind]} project)</span>
                    </Link>
                    {project.managed_in_app && <span className="font-mono text-xs text-info">edited in app</span>}
                  </li>
                ))}
              </ul>
            )}

            <ul className="mt-3 space-y-4">
              {course.modules.map((module) => (
                <li key={module.id}>
                  <div className="flex flex-wrap items-baseline gap-3">
                    <span className="text-sm">{module.title}</span>
                    <Link to={`/manage/modules/${module.id}/lessons/new`} className="font-mono text-xs text-signal underline underline-offset-4">
                      Add lesson
                    </Link>
                  </div>
                  {module.lessons.length > 0 && (
                    <ul className="mt-1 border-l border-rule pl-3 text-sm">
                      {module.lessons.map((lesson) => (
                        <li key={lesson.id} className="grid grid-cols-[minmax(0,1fr)_auto] gap-3 py-0.5">
                          <Link to={`/manage/lessons/${lesson.id}`} className="hover:text-signal">{lesson.title}</Link>
                          <span className="font-mono text-xs text-ink-muted">
                            {lesson.status}, {lesson.exercise_count} exercises{lesson.managed_in_app ? ", edited in app" : ""}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          </details>
        ))}
      </div>
    </div>
  );
}
