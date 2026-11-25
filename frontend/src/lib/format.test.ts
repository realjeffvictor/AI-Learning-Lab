import { describe, expect, it } from "vitest";

import { formatDuration } from "./format";

describe("formatDuration", () => {
  it("handles no time and tiny amounts", () => {
    expect(formatDuration(0)).toBe("none yet");
    expect(formatDuration(45)).toBe("under 1 min");
  });

  it("formats minutes", () => {
    expect(formatDuration(60)).toBe("1 min");
    expect(formatDuration(59 * 60 + 59)).toBe("59 min");
  });

  it("formats hours with padded minutes", () => {
    expect(formatDuration(3600)).toBe("1 h 00 min");
    expect(formatDuration(3600 + 5 * 60)).toBe("1 h 05 min");
  });
});
