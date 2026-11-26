import { useQuery } from "@tanstack/react-query";

import { ErrorNote, Loading } from "../../components/StateMessage";
import { fetchExercises } from "./api";
import { ExerciseCard } from "./ExerciseCard";

export function ExerciseSection({ lessonId }: { lessonId: string | null }) {
  const exercises = useQuery({
    queryKey: ["exercises", lessonId],
    queryFn: ({ signal }) => fetchExercises(lessonId as string, signal),
    enabled: Boolean(lessonId),
  });

  if (!lessonId) return null;
  if (exercises.isPending) return <Loading label="Loading practice" />;
  if (exercises.isError) return <ErrorNote error={exercises.error} />;

  return (
    <section aria-labelledby="practice-heading" className="mt-12">
      <h2 id="practice-heading" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
        Practice
      </h2>
      {exercises.data.length === 0 ? (
        <p className="mt-2 text-sm text-ink-muted">No exercises for this lesson yet.</p>
      ) : (
        <div className="mt-2">
          {exercises.data.map((exercise) => (
            <ExerciseCard key={exercise.id} exercise={exercise} lessonId={lessonId} />
          ))}
        </div>
      )}
    </section>
  );
}
