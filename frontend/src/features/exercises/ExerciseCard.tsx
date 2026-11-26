import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { ErrorNote } from "../../components/StateMessage";
import { LessonMarkdown } from "../curriculum/LessonMarkdown";
import { submitExercise } from "./api";
import { AttemptHistory } from "./AttemptHistory";
import { CodeExercise } from "./CodeExercise";
import { PuzzleExercise } from "./PuzzleExercise";
import { QuizExercise } from "./QuizExercise";
import { ResultPanel } from "./ResultPanel";
import type { ExercisePublic, SubmissionResult } from "./types";

const KIND_LABEL = { code: "Code", quiz: "Quiz", puzzle: "Puzzle" } as const;

export function ExerciseCard({ exercise, lessonId }: { exercise: ExercisePublic; lessonId: string }) {
  const queryClient = useQueryClient();
  const [result, setResult] = useState<SubmissionResult | null>(null);

  const mutation = useMutation({
    mutationFn: (answer: Record<string, unknown>) => submitExercise(exercise.id, answer),
    onSuccess: (data) => {
      setResult(data);
      void queryClient.invalidateQueries({ queryKey: ["exercises", lessonId] });
      void queryClient.invalidateQueries({ queryKey: ["history", exercise.id] });
      void queryClient.invalidateQueries({ queryKey: ["mastery"] });
    },
  });

  const props = { exercise, submit: (answer: Record<string, unknown>) => mutation.mutate(answer), busy: mutation.isPending, result };

  return (
    <article className="border-t border-rule py-6" aria-label={exercise.title}>
      <div className="flex flex-wrap items-baseline gap-3">
        <span className="font-mono text-xs uppercase tracking-widest text-signal">{KIND_LABEL[exercise.kind]}</span>
        <h3 className="font-serif text-xl">{exercise.title}</h3>
        <span className="ml-auto font-mono text-xs text-ink-muted">
          {exercise.attempts === 0
            ? "not attempted"
            : `best ${exercise.best_score}/100${exercise.passed ? ", passed" : ""}`}
        </span>
      </div>
      <div className="mt-3">
        <LessonMarkdown source={exercise.instructions_md} />
      </div>
      <div className="mt-4">
        {exercise.kind === "quiz" && <QuizExercise {...props} />}
        {exercise.kind === "code" && <CodeExercise {...props} />}
        {exercise.kind === "puzzle" && <PuzzleExercise {...props} />}
      </div>
      {mutation.isError && (
        <div className="mt-3">
          <ErrorNote error={mutation.error} />
        </div>
      )}
      {result && <ResultPanel result={result} />}
      <AttemptHistory exerciseId={exercise.id} attempts={exercise.attempts} />
    </article>
  );
}
