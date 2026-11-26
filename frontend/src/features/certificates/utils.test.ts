import { describe, expect, it } from "vitest";

import { unmet, verifyPath } from "./utils";

describe("unmet", () => {
  it("returns only requirements that are not complete", () => {
    const requirements = [
      { key: "lessons", label: "Lessons", done: 2, total: 2 },
      { key: "exercises", label: "Exercises", done: 0, total: 3 },
      { key: "projects", label: "Projects", done: 0, total: 0 },
    ];
    expect(unmet(requirements).map((item) => item.key)).toEqual(["exercises"]);
    expect(unmet([])).toEqual([]);
  });
});

describe("verifyPath", () => {
  it("encodes the code", () => {
    expect(verifyPath("abc_DEF-123")).toBe("/verify/abc_DEF-123");
    expect(verifyPath("a/b")).toBe("/verify/a%2Fb");
  });
});
