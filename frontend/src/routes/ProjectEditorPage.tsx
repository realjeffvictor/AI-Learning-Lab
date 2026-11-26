import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Button } from "../components/Button";
import { Field } from "../components/Field";
import { ErrorNote, Loading } from "../components/StateMessage";
import { LessonMarkdown } from "../features/curriculum/LessonMarkdown";
import { fetchProjectEdit, updateProject } from "../features/manage/api";
import type { ProjectEdit } from "../features/manage/types";
import { KIND_LABEL } from "../features/projects/utils";

const AREA = "rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink";

function ProjectForm({ initial }: { initial: ProjectEdit }) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState(initial.title);
  const [summary, setSummary] = useState(initial.summary);
  const [brief, setBrief] = useState(initial.brief_md);
  const [preview, setPreview] = useState(false);
  const save = useMutation({
    mutationFn: () => updateProject(initial.id, { title, summary, brief_md: brief }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["manage"] }),
  });

  return (
    <div className="max-w-3xl">
      <nav aria-label="Breadcrumb" className="font-mono text-xs text-ink-muted">
        <Link to="/manage/content" className="hover:text-ink">Content</Link> / {initial.course_title}
      </nav>
      <h1 className="mt-3 font-serif text-3xl">Edit project</h1>
      <p className="mt-1 font-mono text-xs text-ink-muted">
        {KIND_LABEL[initial.kind]} project{initial.managed_in_app ? ". Edited in app." : "."}
      </p>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          save.mutate();
        }}
        className="mt-6 flex flex-col gap-5"
      >
        <Field label="Title" name="title" value={title} maxLength={200} onChange={(event) => setTitle(event.target.value)} />
        <Field label="Summary" name="summary" value={summary} maxLength={500} onChange={(event) => setSummary(event.target.value)} />
        <div className="flex flex-col gap-1">
          <div className="flex items-baseline justify-between">
            <label htmlFor="brief" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Brief (Markdown)</label>
            <button type="button" onClick={() => setPreview(!preview)} className="font-mono text-xs text-signal underline underline-offset-4">
              {preview ? "Edit" : "Preview"}
            </button>
          </div>
          {preview ? (
            <div className="border border-rule p-4"><LessonMarkdown source={brief || "(empty)"} /></div>
          ) : (
            <textarea id="brief" rows={22} value={brief} onChange={(event) => setBrief(event.target.value)} className={`${AREA} font-mono text-sm`} />
          )}
        </div>
        <div className="flex items-center gap-3">
          <Button type="submit" disabled={!title.trim() || !brief.trim() || save.isPending}>{save.isPending ? "Saving..." : "Save project"}</Button>
          {save.isSuccess && <span className="text-sm text-ok">Saved.</span>}
        </div>
        {save.isError && <ErrorNote error={save.error} />}
      </form>

      <section className="mt-10" aria-label="Requirements">
        <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Requirements (read only)</p>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
          {initial.requirements.map((item) => <li key={item.id}>{item.text}</li>)}
        </ul>
        <p className="mt-2 text-xs text-ink-muted">
          Requirements stay in the project files, because learners' ticked boxes and submissions refer to them.
        </p>
      </section>
    </div>
  );
}

export function ProjectEditorPage() {
  const { projectId } = useParams();
  const project = useQuery({
    queryKey: ["manage", "project", projectId],
    queryFn: ({ signal }) => fetchProjectEdit(projectId as string, signal),
    enabled: Boolean(projectId),
  });
  if (project.isPending) return <Loading label="Loading project" />;
  if (project.isError) return <ErrorNote error={project.error} />;
  return <ProjectForm key={project.data.id} initial={project.data} />;
}
