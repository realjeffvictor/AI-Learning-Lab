import type { Concept } from "../curriculum/types";
import type { CodeTest } from "../python/pythonRunner";

export type ExerciseKind = "code" | "quiz" | "puzzle";

export interface QuizQuestion {
  id: string;
  prompt: string;
  options: string[];
}
export interface QuizDefinition {
  questions: QuizQuestion[];
}
export interface CodeDefinition {
  starter_code: string;
  timeout_seconds: number;
  tests: CodeTest[];
}
export interface PuzzleItem {
  id: string;
  text: string;
}
export interface PuzzleDefinition {
  puzzle_type: "order";
  items: PuzzleItem[];
}

export interface ExercisePublic {
  id: string;
  slug: string;
  title: string;
  kind: ExerciseKind;
  position: number;
  instructions_md: string;
  pass_score: number;
  concepts: Concept[];
  definition: Record<string, unknown>;
  attempts: number;
  best_score: number | null;
  passed: boolean;
}

export interface FeedbackItem {
  id: string;
  correct: boolean;
  message: string | null;
  correct_index: number | null;
}
export interface ConceptResult {
  slug: string;
  name: string;
  correct: number;
  total: number;
}
export interface Recommendation {
  type: "lesson" | "resource";
  concept_slug: string;
  concept_name: string;
  title: string;
  course_slug: string | null;
  module_slug: string | null;
  lesson_slug: string | null;
  url: string | null;
  resource_kind: string | null;
  is_open_source: boolean | null;
}
export interface SubmissionResult {
  id: string;
  score: number;
  passed: boolean;
  pass_score: number;
  attempt_number: number;
  feedback: FeedbackItem[];
  concept_results: ConceptResult[];
  recommendations: Recommendation[];
  created_at: string;
}
export interface SubmissionSummary {
  id: string;
  score: number;
  passed: boolean;
  created_at: string;
}
export interface Mastery {
  slug: string;
  name: string;
  category: "A" | "B" | "C";
  correct: number;
  total: number;
}

export interface ExerciseProps {
  exercise: ExercisePublic;
  submit: (answer: Record<string, unknown>) => void;
  busy: boolean;
  result: SubmissionResult | null;
}
