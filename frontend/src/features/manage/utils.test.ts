import { describe, expect, it } from "vitest";

import { DEFINITION_TEMPLATES, linesToList, parseDefinition, passRate, toggle } from "./utils";

describe("linesToList", () => {
  it("trims and drops blank lines", () => {
    expect(linesToList("  a \n\n b\n   \n")).toEqual(["a", "b"]);
    expect(linesToList("")).toEqual([]);
  });
});

describe("toggle", () => {
  it("adds and removes without mutating", () => {
    const original = ["a"];
    expect(toggle(original, "b")).toEqual(["a", "b"]);
    expect(toggle(original, "a")).toEqual([]);
    expect(original).toEqual(["a"]);
  });
});

describe("parseDefinition", () => {
  it("accepts objects only", () => {
    expect(parseDefinition('{"a":1}')).toEqual({ ok: true, value: { a: 1 } });
    expect(parseDefinition("[1]").ok).toBe(false);
    expect(parseDefinition("null").ok).toBe(false);
    expect(parseDefinition("{oops").ok).toBe(false);
  });

  it("accepts every built-in template", () => {
    for (const template of Object.values(DEFINITION_TEMPLATES)) expect(parseDefinition(template).ok).toBe(true);
  });
});

describe("passRate", () => {
  it("handles zero learners and rounds", () => {
    expect(passRate(0, 0)).toBe("none");
    expect(passRate(1, 3)).toBe("33%");
  });
});
