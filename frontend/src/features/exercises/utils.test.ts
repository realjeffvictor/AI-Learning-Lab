import { describe, expect, it } from "vitest";

import { allAnswered, moveItem, percent } from "./utils";

describe("moveItem", () => {
  it("moves an item down and up", () => {
    expect(moveItem(["a", "b", "c"], 0, 1)).toEqual(["b", "a", "c"]);
    expect(moveItem(["a", "b", "c"], 2, -1)).toEqual(["a", "c", "b"]);
  });

  it("ignores moves past either end and never mutates the input", () => {
    const original = ["a", "b"];
    expect(moveItem(original, 0, -1)).toEqual(["a", "b"]);
    expect(moveItem(original, 1, 1)).toEqual(["a", "b"]);
    expect(moveItem(original, 5, 1)).toEqual(["a", "b"]);
    expect(original).toEqual(["a", "b"]);
  });
});

describe("allAnswered", () => {
  it("requires every question, including index 0", () => {
    expect(allAnswered(["q1", "q2"], { q1: 0 })).toBe(false);
    expect(allAnswered(["q1", "q2"], { q1: 0, q2: 2 })).toBe(true);
    expect(allAnswered([], {})).toBe(true);
  });
});

describe("percent", () => {
  it("rounds and handles zero totals", () => {
    expect(percent(1, 3)).toBe(33);
    expect(percent(0, 0)).toBe(0);
  });
});
