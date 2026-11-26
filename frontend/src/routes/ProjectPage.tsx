import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { ErrorNote, Loading } from "../components/StateMessage";
import { fetchProject } from "../features/projects/api";
import { ProjectWorkspace } from "../features/projects/ProjectWorkspace";

export function ProjectPage() {
  const { courseSlug, projectSlug } = useParams();
  const project = useQuery({
    queryKey: ["project", courseSlug, projectSlug],
    queryFn: ({ signal }) => fetchProject(courseSlug as string, projectSlug as string, signal),
    enabled: Boolean(courseSlug && projectSlug),
  });
  if (project.isPending) return <Loading label="Loading project" />;
  if (project.isError) return <ErrorNote error={project.error} />;
  return <ProjectWorkspace key={project.data.id} detail={project.data} />;
}
