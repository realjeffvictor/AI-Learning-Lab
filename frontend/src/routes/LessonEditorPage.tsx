import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { Button } from "../components/Button";
import { Field } from "../components/Field";
import { ErrorNote, Loading } from "../components/StateMessage";
import { LessonMarkdown } from "../features/curriculum/LessonMarkdown";
import { createLesson, fetchConcepts, fetchLessonEdit, fetchManageExercises, updateLesson } from "../features/manage/api";
import { ConceptPicker } from "../features/manage/ConceptPicker";
import type { LessonEdit, LessonWrite } from "../features/manage/types";
import { linesToList, toggle } from "../features/manage/utils";
import { PRINCIPLES } from "../lib/principles";

const AREA = "rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink";

function LessonExercises({ lessonId, published }: { lessonId: string; published: boolean }) {
  const exercises = useQuery({ queryKey: ["manage", "exercises", lessonId], queryFn: ({ signal }) => fetchManageExercises(lessonId, signal) });
  return (
    <section className="mt-12 border-t border-rule pt-6" aria-labelledby="ex-heading">
      <h2 id="ex-heading" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Exercises</h2>
      {exercises.isPending && <Loading label="Loading" />}
      {exercises.isError && <ErrorNote error={exercises.error} />}
      {exercises.data && (
        <ul className="mt-2 divide-y divide-rule border-y border-rule text-sm">
          {exercises.data.map((item) => (
            <li key={item.id} className="grid grid-cols-[minmax(0,1fr)_auto] gap-3 py-2">
              <Link to={`/manage/exercises/${item.id}`} className="hover:text-signal">{item.title}</Link>
              <span className="font-mono text-xs text-ink-muted">{item.kind}, {item.attempts} attempts</span>
            </li>
          ))}
          {exercises.data.length === 0 && <li className="py-2 text-ink-muted">No exercises yet.</li>}
        </ul>
      )}
      {published ? (
        <Link to={`/manage/lessons/${lessonId}/exercises/new`} className="mt-3 inline-block text-sm text-signal underline underline-offset-4">
          Add exercise
        </Link>
      ) : (
        <p className="mt-2 text-xs text-ink-muted">Write the lesson text and save before adding exercises.</p>
      )}
    </section>
  );
}

function LessonForm({ initial, moduleId }: { initial: LessonEdit | null; moduleId: string | null }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const concepts = useQuery({ queryKey: ["manage", "concepts"], queryFn: ({ signal }) => fetchConcepts(signal) });

  const [slug, setSlug] = useState("");
  const [title, setTitle] = useState(initial?.title ?? "");
  const [summary, setSummary] = useState(initial?.summary ?? "");
  const [minutes, setMinutes] = useState(String(initial?.minutes ?? 10));
  const [objectives, setObjectives] = useState((initial?.objectives ?? []).join("\n"));
  const [principles, setPrinciples] = useState<string[]>(initial?.principles ?? []);
  const [selected, setSelected] = useState<string[]>(initial?.concepts ?? []);
  const [content, setContent] = useState(initial?.content_md ?? "");
  const [preview, setPreview] = useState(false);

  const body = (): LessonWrite => ({
    title,
    summary,
    minutes: Number(minutes),
    objectives: linesToList(objectives),
    principles,
    concepts: selected,
    content_md: content.trim() ? content : null,
  });

  const save = useMutation({
    mutationFn: () => (initial ? updateLesson(initial.id, body()) : createLesson(moduleId as string, { ...body(), slug })),
    onSuccess: (saved) => {
      void queryClient.invalidateQueries({ queryKey: ["manage"] });
      if (!initial) navigate(`/manage/lessons/${saved.id}`);
    },
  });

  const minutesValue = Number(minutes);
  const valid = title.trim() !== "" && Number.isInteger(minutesValue) && minutesValue >= 1 && minutesValue <= 240 && (initial !== null || slug.trim() !== "");
  const status = save.data?.status ?? initial?.status ?? "planned";

  return (
    <div className="max-w-3xl">
      <nav aria-label="Breadcrumb" className="font-mono text-xs text-ink-muted">
        <Link to="/manage/content" className="hover:text-ink">Content</Link>
        {initial && <> / {initial.course_title} / {initial.module_title}</>}
      </nav>
      <h1 className="mt-3 font-serif text-3xl">{initial ? "Edit lesson" : "New lesson"}</h1>
      <p className="mt-1 font-mono text-xs text-ink-muted">
        {status === "published" ? "Published: learners can open it." : "Planned: shown in the outline only until it has text."}
        {initial?.managed_in_app ? " Edited in app." : ""}
      </p>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          save.mutate();
        }}
        className="mt-6 flex flex-col gap-5"
      >
        {!initial && (
          <Field label="Slug" name="slug" value={slug} maxLength={80} onChange={(event) => setSlug(event.target.value)}
            hint="Lowercase letters, digits and hyphens. It becomes part of the lesson address and cannot be changed later." />
        )}
        <Field label="Title" name="title" value={title} maxLength={200} onChange={(event) => setTitle(event.target.value)} />
        <Field label="Summary" name="summary" value={summary} maxLength={500} onChange={(event) => setSummary(event.target.value)} />
        <Field label="Estimated minutes" name="minutes" type="number" min={1} max={240} value={minutes} onChange={(event) => setMinutes(event.target.value)} />

        <div className="flex flex-col gap-1">
          <label htmlFor="objectives" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Learning objectives</label>
          <textarea id="objectives" rows={4} value={objectives} onChange={(event) => setObjectives(event.target.value)} className={AREA} />
          <p className="text-xs text-ink-muted">One per line, up to 8.</p>
        </div>

        <fieldset>
          <legend className="font-mono text-xs uppercase tracking-widest text-ink-muted">Principles practised</legend>
          <div className="mt-1 flex flex-wrap gap-4">
            {PRINCIPLES.map(([letter, name]) => (
              <label key={letter} className="flex cursor-pointer items-center gap-2 text-sm">
                <input type="checkbox" checked={principles.includes(letter)} onChange={() => setPrinciples(toggle(principles, letter))} />
                {letter} {name}
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend className="font-mono text-xs uppercase tracking-widest text-ink-muted">Concepts covered</legend>
          <div className="mt-2">
            {concepts.isPending && <Loading label="Loading concepts" />}
            {concepts.data && <ConceptPicker options={concepts.data} selected={selected} onChange={setSelected} />}
          </div>
        </fieldset>

        <div className="flex flex-col gap-1">
          <div className="flex items-baseline justify-between">
            <label htmlFor="content" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Lesson text (Markdown)</label>
            <button type="button" onClick={() => setPreview(!preview)} className="font-mono text-xs text-signal underline underline-offset-4">
              {preview ? "Edit" : "Preview"}
            </button>
          </div>
          {preview ? (
            <div className="border border-rule p-4"><LessonMarkdown source={content || "(empty)"} /></div>
          ) : (
            <textarea id="content" rows={20} value={content} onChange={(event) => setContent(event.target.value)} className={`${AREA} font-mono text-sm`} />
          )}
          <p className="text-xs text-ink-muted">
            Leave empty to keep the lesson as Planned. Once a lesson has text, it can no longer be emptied. Raw HTML is not rendered.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button type="submit" disabled={!valid || save.isPending}>{save.isPending ? "Saving..." : "Save lesson"}</Button>
          {save.isSuccess && initial && <span className="text-sm text-ok">Saved.</span>}
        </div>
        {save.isError && <ErrorNote error={save.error} />}
      </form>

      {initial && <LessonExercises lessonId={initial.id} published={status === "published"} />}
    </div>
  );
}

export function LessonEditorPage() {
  const { lessonId, moduleId } = useParams();
  const lesson = useQuery({
    queryKey: ["manage", "lesson", lessonId],
    queryFn: ({ signal }) => fetchLessonEdit(lessonId as string, signal),
    enabled: Boolean(lessonId),
  });
  if (!lessonId) return <LessonForm key="new" initial={null} moduleId={moduleId ?? null} />;
  if (lesson.isPending) return <Loading label="Loading lesson" />;
  if (lesson.isError) return <ErrorNote error={lesson.error} />;
  return <LessonForm key={lesson.data.id} initial={lesson.data} moduleId={null} />;
}
