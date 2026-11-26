import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { fetchExercises } from "../exercises/api";
import { AssistantPanel } from "./AssistantPanel";

/** Collapsed by default, and nothing is fetched until the learner opens it. */
export function AssistantSection({ lessonId }: { lessonId: string | null }) {
  const [opened, setOpened] = useState(false);
  const exercises = useQuery({
    queryKey: ["exercises", lessonId],
    queryFn: ({ signal }) => fetchExercises(lessonId as string, signal),
    enabled: Boolean(lessonId) && opened,
  });

  if (!lessonId) return null;
  return (
    <details
      className="mt-12 border-t border-rule pt-4"
      onToggle={(event) => {
        if (event.currentTarget.open) setOpened(true);
      }}
    >
      <summary className="cursor-pointer font-mono text-xs uppercase tracking-widest text-ink-muted">
        Ask the AI about this lesson
      </summary>
      {opened && (
        <div className="mt-4">
          <AssistantPanel
            lessonId={lessonId}
            exercises={(exercises.data ?? []).map((item) => ({ id: item.id, title: item.title }))}
          />
        </div>
      )}
    </details>
  );
}
