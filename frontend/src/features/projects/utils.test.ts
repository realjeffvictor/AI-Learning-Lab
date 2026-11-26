import { describe, expect, it } from "vitest";

import { checklistProgress, isEditable, isGithubRepo, submitProblems } from "./utils";

const requirements = [
  { id: "a", text: "A" },
  { id: "b", text: "B" },
];
const rules = { kind: "build" as const, requirements, minDocumentation: 10, minReflection: 5 };
const complete = { repoUrl: "https://github.com/x/y", documentation: "x".repeat(10), reflection: "y".repeat(5), checks: { a: true, b: true } };

describe("isEditable", () => {
  it("allows editing before submission and after a change request only", () => {
    expect(isEditable("not_started")).toBe(true);
    expect(isEditable("draft")).toBe(true);
    expect(isEditable("changes_requested")).toBe(true);
    expect(isEditable("submitted")).toBe(false);
    expect(isEditable("approved")).toBe(false);
  });
});

describe("checklistProgress", () => {
  it("counts ticked requirements and ignores unknown ids", () => {
    expect(checklistProgress(requirements, { a: true, zzz: true })).toEqual({ done: 1, total: 2 });
    expect(checklistProgress([], {})).toEqual({ done: 0, total: 0 });
  });
});

describe("submitProblems", () => {
  it("reports every missing piece for a build project", () => {
    const problems = submitProblems({ repoUrl: " ", documentation: "", reflection: "", checks: {} }, rules);
    expect(problems).toHaveLength(4);
  });

  it("is empty when everything is in place", () => {
    expect(submitProblems(complete, rules)).toEqual([]);
  });

  it("does not ask for a repository on other project kinds", () => {
    const problems = submitProblems({ ...complete, repoUrl: "" }, { ...rules, kind: "architecture" });
    expect(problems).toEqual([]);
  });

  it("measures trimmed text", () => {
    expect(submitProblems({ ...complete, documentation: "   short   " }, rules)).toHaveLength(1);
  });
});

describe("isGithubRepo", () => {
  it("accepts GitHub repositories only", () => {
    expect(isGithubRepo("https://github.com/alice/project")).toBe(true);
    expect(isGithubRepo("https://evil.example/alice/project")).toBe(false);
    expect(isGithubRepo("javascript:alert(1)")).toBe(false);
    expect(isGithubRepo(null)).toBe(false);
  });
});
