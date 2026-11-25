import { describe, expect, it } from "vitest";

import { buildTicks } from "./trace";

describe("buildTicks", () => {
  it("returns nothing for an empty outline", () => {
    expect(buildTicks({ published: 0, completed: 0, planned: 0 })).toEqual([]);
  });

  it("orders done, open, planned", () => {
    expect(buildTicks({ published: 3, completed: 1, planned: 2 })).toEqual([
      "done", "open", "open", "planned", "planned",
    ]);
  });

  it("never reports more done than published", () => {
    const ticks = buildTicks({ published: 2, completed: 5, planned: 0 });
    expect(ticks).toEqual(["done", "done"]);
  });

  it("scales long outlines and keeps every non-empty category visible", () => {
    const ticks = buildTicks({ published: 90, completed: 30, planned: 120 }, 40);
    expect(ticks.length).toBeLessThanOrEqual(42);
    expect(new Set(ticks)).toEqual(new Set(["done", "open", "planned"]));
  });
});
