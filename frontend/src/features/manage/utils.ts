import type { ExerciseKind } from "../exercises/types";

export function linesToList(text: string): string[] {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

export function toggle<T>(items: readonly T[], value: T): T[] {
  return items.includes(value) ? items.filter((item) => item !== value) : [...items, value];
}

export type ParsedDefinition = { ok: true; value: Record<string, unknown> } | { ok: false; error: string };

export function parseDefinition(text: string): ParsedDefinition {
  try {
    const value: unknown = JSON.parse(text);
    if (value === null || typeof value !== "object" || Array.isArray(value)) {
      return { ok: false, error: "The definition must be a JSON object." };
    }
    return { ok: true, value: value as Record<string, unknown> };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? `Invalid JSON: ${error.message}` : "Invalid JSON." };
  }
}

export function passRate(passedLearners: number, learners: number): string {
  return learners === 0 ? "none" : `${Math.round((100 * passedLearners) / learners)}%`;
}

export const DEFINITION_TEMPLATES: Record<ExerciseKind, string> = {
  quiz: JSON.stringify(
    {
      questions: [
        { id: "q1", prompt: "Question text", options: ["First", "Second"], answer: 0, explanation: "Why it is right.", concept: null },
      ],
    },
    null,
    2,
  ),
  code: JSON.stringify(
    {
      starter_code: "# Write your code below\n",
      timeout_seconds: 5,
      tests: [{ id: "t1", description: "Prints hello", type: "stdout", expected_stdout: "hello" }],
    },
    null,
    2,
  ),
  puzzle: JSON.stringify({ puzzle_type: "order", lines: ["first line", "second line", "third line"] }, null, 2),
};
