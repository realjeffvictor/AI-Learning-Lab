import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { ErrorNote, Loading } from "../components/StateMessage";
import { fetchProjects } from "../features/projects/api";
import { ProjectStatusTag } from "../features/projects/ProjectStatusTag";
import { KIND_LABEL } from "../features/projects/utils";

export function ProjectsPage() {
  const projects = useQuery({ queryKey: ["projects"], queryFn: ({ signal }) => fetchProjects(signal) });
  if (projects.isPending) return <Loading label="Loading projects" />;
  if (projects.isError) return <ErrorNote error={projects.error} />;

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Projects</p>
      <h1 className="mt-2 font-serif text-3xl">Practical projects</h1>
      <p className="mt-2 max-w-2xl text-ink-muted">
        Projects are reviewed by a person, not scored by a machine. They show that you understand what you built and can
        maintain it. Only the projects listed here have been written so far.
      </p>

      {projects.data.length === 0 ? (
        <p className="mt-8 text-ink-muted">No projects have been published yet.</p>
      ) : (
        <ul className="mt-8 divide-y divide-rule border-y border-rule">
          {projects.data.map((project) => (
            <li key={project.id} className="grid gap-2 py-4 md:grid-cols-[7rem_minmax(0,1fr)_11rem] md:gap-6">
              <span className="font-mono text-xs uppercase tracking-widest text-signal">{KIND_LABEL[project.kind]}</span>
              <div>
                <Link to={`/projects/${project.course_slug}/${project.slug}`} className="font-serif text-xl hover:text-signal">
                  {project.title}
                </Link>
                <p className="mt-1 max-w-xl text-sm text-ink-muted">{project.summary}</p>
                <p className="mt-1 font-mono text-xs text-ink-muted">
                  {project.course_title}. {project.requirements_count} requirements.
                </p>
              </div>
              <div>
                <ProjectStatusTag status={project.status} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
