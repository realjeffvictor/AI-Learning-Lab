import type { Concept } from "../curriculum/types";

export type ProjectKind = "build" | "architecture" | "code_review";
export type ProjectStatus = "not_started" | "draft" | "submitted" | "approved" | "changes_requested";
export type Outcome = "approved" | "changes_requested";
export type RubricCriterion = "understanding" | "implementation" | "verification" | "ownership";

export interface Requirement {
  id: string;
  text: string;
}

export interface ProjectSummary {
  id: string;
  slug: string;
  title: string;
  summary: string;
  kind: ProjectKind;
  course_slug: string;
  course_title: string;
  status: ProjectStatus;
  requirements_count: number;
}

export interface SubmissionRead {
  id: string;
  status: Exclude<ProjectStatus, "not_started">;
  repo_url: string | null;
  documentation_md: string;
  reflection_md: string;
  requirement_checks: Record<string, boolean>;
  submitted_at: string | null;
  updated_at: string;
}

export interface ReviewRead {
  id: string;
  outcome: Outcome;
  rubric_scores: Record<string, number>;
  feedback: string;
  created_at: string;
  reviewer_name: string | null;
}

export interface ProjectDetail {
  id: string;
  slug: string;
  title: string;
  summary: string;
  kind: ProjectKind;
  course_slug: string;
  course_title: string;
  brief_md: string;
  requirements: Requirement[];
  requires_repo: boolean;
  concepts: Concept[];
  min_documentation_chars: number;
  min_reflection_chars: number;
  submission: SubmissionRead | null;
  reviews: ReviewRead[];
}

export interface SubmissionDraft {
  repo_url?: string | null;
  documentation_md?: string;
  reflection_md?: string;
  requirement_checks?: Record<string, boolean>;
}

export interface QueueItem {
  submission_id: string;
  project_title: string;
  project_kind: ProjectKind;
  course_slug: string;
  course_title: string;
  learner_name: string;
  learner_email: string;
  submitted_at: string;
}

export interface QueuePage {
  items: QueueItem[];
  page: number;
  page_size: number;
  total: number;
}

export interface ReviewDetail {
  submission: SubmissionRead;
  project_title: string;
  project_kind: ProjectKind;
  course_slug: string;
  course_title: string;
  brief_md: string;
  requirements: Requirement[];
  learner_name: string;
  learner_email: string;
  reviews: ReviewRead[];
}

export interface ReviewPayload {
  outcome: Outcome;
  rubric_scores: Record<RubricCriterion, number>;
  feedback: string;
}

export interface Achievement {
  key: string;
  title: string;
  description: string;
  earned: boolean;
  earned_at: string | null;
}

export const RUBRIC: { key: RubricCriterion; label: string; hint: string }[] = [
  { key: "understanding", label: "Understanding", hint: "Can explain how it works and why." },
  { key: "implementation", label: "Implementation", hint: "Meets the requirements and is clear and maintainable." },
  { key: "verification", label: "Verification", hint: "Shows testing, checking and critical review of AI output." },
  { key: "ownership", label: "Ownership", hint: "Could maintain and change it without the AI." },
];

export const SCORE_LABEL: Record<number, string> = { 1: "Not yet", 2: "Developing", 3: "Solid", 4: "Strong" };
