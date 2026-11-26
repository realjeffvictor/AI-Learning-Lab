import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { Button } from "../components/Button";
import { Field } from "../components/Field";
import { ErrorNote, Loading } from "../components/StateMessage";
import type { ExerciseKind } from "../features/exercises/types";
import { createExercise, deleteExercise, fetchConcepts, fetchExerciseEdit, updateExercise } from "../features/manage/api";
import { ConceptPicker } from "../features/manage/ConceptPicker";
import type { ExerciseEdit } from "../features/manage/types";
import { DEFINITION_TEMPLATES, parseDefinition } from "../features/manage/utils";

const AREA = "rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink";

function ExerciseForm({ initial, lessonId }: { initial: ExerciseEdit | null; lessonId: string }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const concepts = useQuery({ queryKey: ["manage", "concepts"], queryFn: ({ signal }) => fetchConcepts(signal) });

  const [kind, setKind] = useState<ExerciseKind>(initial?.kind ?? "quiz");
  const [slug, setSlug] = useState("");
  const [title, setTitle] = useState(initial?.title ?? "");
  const [instructions, setInstructions] = useState(initial?.instructions_md ?? "");
  const [passScore, setPassScore] = useState(String(initial?.pass_score ?? 70));
  const [selected, setSelected] = useState<string[]>(initial?.concepts ?? []);
  const [definition, setDefinition] = useState(
    initial ? JSON.stringify(initial.definition, null, 2) : DEFINITION_TEMPLATES.quiz,
  );
  const [localError, setLocalError] = useState<string | null>(null);

  const refresh = () => queryClient.invalidateQueries({ queryKey: ["manage"] });
  const save = useMutation({
    mutationFn: () => {
      const parsed = parseDefinition(definition);
      if (!parsed.ok) return Promise.reject(new Error(parsed.error));
      const common = { title, instructions_md: instructions, pass_score: Number(passScore), concepts: selected, definition: parsed.value };
      return initial ? updateExercise(initial.id, common) : createExercise(lessonId, { ...common, slug, kind });
    },
    onSuccess: (saved) => {
      setLocalError(null);
      void refresh();
      if (!initial) navigate(`/manage/exercises/${saved.id}`);
    },
    onError: (error) => setLocalError(error instanceof Error && !("code" in error) ? error.message : null),
  });
  const remove = useMutation({
    mutationFn: () => deleteExercise((initial as ExerciseEdit).id),
    onSuccess: () => {
      void refresh();
      navigate(`/manage/lessons/${lessonId}`);
    },
  });

  const score = Number(passScore);
  const valid = title.trim() !== "" && instructions.trim() !== "" && selected.length > 0 && Number.isInteger(score) && score >= 1 && score <= 100 && (initial !== null || slug.trim() !== "");

  return (
    <div className="max-w-3xl">
      <nav aria-label="Breadcrumb" className="font-mono text-xs text-ink-muted">
        <Link to="/manage/content" className="hover:text-ink">Content</Link> /{" "}
        <Link to={`/manage/lessons/${lessonId}`} className="hover:text-ink">{initial?.lesson_title ?? "Lesson"}</Link>
      </nav>
      <h1 className="mt-3 font-serif text-3xl">{initial ? "Edit exercise" : "New exercise"}</h1>
      {initial && (
        <p className="mt-1 font-mono text-xs text-ink-muted">
          {initial.kind}. {initial.attempts} learner attempts. Changing it changes what past scores meant.
        </p>
      )}

      <form
        onSubmit={(event) => {
          event.preventDefault();
          save.mutate();
        }}
        className="mt-6 flex flex-col gap-5"
      >
        {!initial && (
          <div className="grid gap-5 sm:grid-cols-2">
            <Field label="Slug" name="slug" value={slug} maxLength={40} onChange={(event) => setSlug(event.target.value)} hint="Lowercase letters, digits, hyphens and underscores." />
            <div className="flex flex-col gap-1">
              <label htmlFor="kind" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Type</label>
              <select
                id="kind"
                value={kind}
                onChange={(event) => {
                  const next = event.target.value as ExerciseKind;
                  setKind(next);
                  setDefinition(DEFINITION_TEMPLATES[next]);
                }}
                className={AREA}
              >
                <option value="quiz">Quiz</option>
                <option value="code">Code</option>
                <option value="puzzle">Puzzle (order the lines)</option>
              </select>
            </div>
          </div>
        )}
        <Field label="Title" name="title" value={title} maxLength={200} onChange={(event) => setTitle(event.target.value)} />
        <div className="flex flex-col gap-1">
          <label htmlFor="instructions" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Instructions (Markdown)</label>
          <textarea id="instructions" rows={5} maxLength={5000} value={instructions} onChange={(event) => setInstructions(event.target.value)} className={AREA} />
        </div>
        <Field label="Pass score (1 to 100)" name="pass" type="number" min={1} max={100} value={passScore} onChange={(event) => setPassScore(event.target.value)} />
        <fieldset>
          <legend className="font-mono text-xs uppercase tracking-widest text-ink-muted">Concepts (at least one)</legend>
          <div className="mt-2">
            {concepts.isPending && <Loading label="Loading concepts" />}
            {concepts.data && <ConceptPicker options={concepts.data} selected={selected} onChange={setSelected} />}
          </div>
        </fieldset>
        <div className="flex flex-col gap-1">
          <label htmlFor="definition" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Definition (JSON)</label>
          <textarea id="definition" rows={18} spellCheck={false} value={definition} onChange={(event) => setDefinition(event.target.value)} className={`${AREA} font-mono text-sm`} />
          <p className="text-xs text-ink-muted">
            Checked by the same rules as the curriculum files. Quiz answers are 0-based option numbers. Concepts named inside questions or tests must be among the concepts above.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Button type="submit" disabled={!valid || save.isPending}>{save.isPending ? "Saving..." : "Save exercise"}</Button>
          {save.isSuccess && initial && <span className="text-sm text-ok">Saved.</span>}
          {initial && (
            <Button
              variant="danger"
              disabled={remove.isPending}
              onClick={() => {
                if (window.confirm("Delete this exercise? This cannot be undone.")) remove.mutate();
              }}
            >
              Delete exercise
            </Button>
          )}
        </div>
        {localError && <p role="alert" className="text-sm text-danger">{localError}</p>}
        {save.isError && !localError && <ErrorNote error={save.error} />}
        {remove.isError && <ErrorNote error={remove.error} />}
      </form>
    </div>
  );
}

export function ExerciseEditorPage() {
  const { exerciseId, lessonId } = useParams();
  const exercise = useQuery({
    queryKey: ["manage", "exercise", exerciseId],
    queryFn: ({ signal }) => fetchExerciseEdit(exerciseId as string, signal),
    enabled: Boolean(exerciseId),
  });
  if (!exerciseId) return <ExerciseForm key="new" initial={null} lessonId={lessonId as string} />;
  if (exercise.isPending) return <Loading label="Loading exercise" />;
  if (exercise.isError) return <ErrorNote error={exercise.error} />;
  return <ExerciseForm key={exercise.data.id} initial={exercise.data} lessonId={exercise.data.lesson_id} />;
}
