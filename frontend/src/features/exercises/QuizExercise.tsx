import { useState } from "react";

import { Button } from "../../components/Button";
import { allAnswered } from "./utils";
import type { ExerciseProps, QuizDefinition } from "./types";

export function QuizExercise({ exercise, submit, busy, result }: ExerciseProps) {
  const definition = exercise.definition as unknown as QuizDefinition;
  const [answers, setAnswers] = useState<Record<string, number | undefined>>({});
  const feedback = new Map(result?.feedback.map((item) => [item.id, item]));
  const ready = allAnswered(
    definition.questions.map((q) => q.id),
    answers,
  );

  return (
    <div>
      <ol className="space-y-6">
        {definition.questions.map((question, index) => {
          const item = feedback.get(question.id);
          return (
            <li key={question.id}>
              <fieldset>
                <legend className="font-medium">
                  <span className="mr-2 font-mono text-xs text-ink-muted">{String(index + 1).padStart(2, "0")}</span>
                  {question.prompt}
                </legend>
                <div className="mt-2 space-y-1 pl-6">
                  {question.options.map((option, optionIndex) => {
                    const chosen = answers[question.id] === optionIndex;
                    const isCorrect = item && item.correct_index === optionIndex;
                    return (
                      <label key={option} className="flex cursor-pointer items-start gap-2 text-sm">
                        <input
                          type="radio"
                          name={`${exercise.id}-${question.id}`}
                          checked={chosen}
                          onChange={() => setAnswers({ ...answers, [question.id]: optionIndex })}
                          className="mt-1"
                        />
                        <span className={isCorrect ? "text-ok" : ""}>
                          {option}
                          {isCorrect && " (correct answer)"}
                        </span>
                      </label>
                    );
                  })}
                </div>
                {item && (
                  <p className={`mt-2 pl-6 text-sm ${item.correct ? "text-ok" : "text-warn"}`}>
                    {item.correct ? "Correct. " : "Not quite. "}
                    <span className="text-ink-muted">{item.message}</span>
                  </p>
                )}
              </fieldset>
            </li>
          );
        })}
      </ol>
      <Button
        className="mt-6"
        disabled={!ready || busy}
        onClick={() => submit({ answers: Object.fromEntries(Object.entries(answers)) })}
      >
        {busy ? "Scoring..." : result ? "Submit again" : "Submit answers"}
      </Button>
    </div>
  );
}
