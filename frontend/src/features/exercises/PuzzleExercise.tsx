import { useMemo, useState } from "react";

import { Button } from "../../components/Button";
import { moveItem } from "./utils";
import type { ExerciseProps, PuzzleDefinition } from "./types";

export function PuzzleExercise({ exercise, submit, busy, result }: ExerciseProps) {
  const definition = exercise.definition as unknown as PuzzleDefinition;
  const texts = useMemo(() => Object.fromEntries(definition.items.map((item) => [item.id, item.text])), [definition.items]);
  const [order, setOrder] = useState<string[]>(() => definition.items.map((item) => item.id));
  const wrong = new Set(result?.feedback.filter((item) => !item.correct).map((item) => item.id));

  return (
    <div>
      <ol className="max-w-xl space-y-1">
        {order.map((id, index) => (
          <li
            key={id}
            className={`grid grid-cols-[1.5rem_minmax(0,1fr)_auto] items-center gap-2 border-l-2 bg-surface-sunk px-3 py-2 ${
              result ? (wrong.has(id) ? "border-warn" : "border-ok") : "border-rule"
            }`}
          >
            <span className="font-mono text-xs text-ink-muted">{index + 1}</span>
            <code className="whitespace-pre-wrap font-mono text-sm">{texts[id]}</code>
            <span className="flex gap-1">
              <Button
                variant="secondary"
                aria-label={`Move "${texts[id]}" up`}
                disabled={index === 0}
                onClick={() => setOrder(moveItem(order, index, -1))}
              >
                Up
              </Button>
              <Button
                variant="secondary"
                aria-label={`Move "${texts[id]}" down`}
                disabled={index === order.length - 1}
                onClick={() => setOrder(moveItem(order, index, 1))}
              >
                Down
              </Button>
            </span>
          </li>
        ))}
      </ol>
      <Button className="mt-4" disabled={busy} onClick={() => submit({ order })}>
        {busy ? "Scoring..." : result ? "Submit again" : "Check order"}
      </Button>
    </div>
  );
}
