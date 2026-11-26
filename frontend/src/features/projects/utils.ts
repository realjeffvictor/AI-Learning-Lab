import type { ProjectKind, ProjectStatus, Requirement } from "./types";

export const KIND_LABEL: Record<ProjectKind, string> = {
  build: "Build",
  architecture: "Architecture",
  code_review: "Code review",
};

export const STATUS_LABEL: Record<ProjectStatus, string> = {
  not_started: "Not started",
  draft: "Draft",
  submitted: "Awaiting review",
  approved: "Approved",
  changes_requested: "Changes requested",
};

export const DOCUMENTATION_LABEL: Record<ProjectKind, string> = {
  build: "README and documentation",
  architecture: "Architecture decision record",
  code_review: "Your review",
};

/** Mirrors the server: a submission can be edited until it is submitted, and again if changes are requested. */
export function isEditable(status: ProjectStatus): boolean {
  return status === "not_started" || status === "draft" || status === "changes_requested";
}

export function checklistProgress(requirements: Requirement[], checks: Record<string, boolean>) {
  return { done: requirements.filter((item) => checks[item.id]).length, total: requirements.length };
}

export interface DraftValues {
  repoUrl: string;
  documentation: string;
  reflection: string;
  checks: Record<string, boolean>;
}

export interface SubmitRules {
  kind: ProjectKind;
  requirements: Requirement[];
  minDocumentation: number;
  minReflection: number;
}

/** Friendly pre-check. The server runs the same rules and is the authority. */
export function submitProblems(values: DraftValues, rules: SubmitRules): string[] {
  const problems: string[] = [];
  if (rules.kind === "build" && !values.repoUrl.trim()) problems.push("Add your GitHub repository link.");
  const { done, total } = checklistProgress(rules.requirements, values.checks);
  if (done < total) problems.push(`Tick every requirement you have met (${total - done} left).`);
  const docLength = values.documentation.trim().length;
  if (docLength < rules.minDocumentation) {
    problems.push(`Documentation needs at least ${rules.minDocumentation} characters (you have ${docLength}).`);
  }
  const reflectionLength = values.reflection.trim().length;
  if (reflectionLength < rules.minReflection) {
    problems.push(`Reflection needs at least ${rules.minReflection} characters (you have ${reflectionLength}).`);
  }
  return problems;
}

/** Only link out to GitHub repositories. Anything else is shown as plain text. */
export function isGithubRepo(url: string | null): url is string {
  return Boolean(url && /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+$/.test(url));
}
