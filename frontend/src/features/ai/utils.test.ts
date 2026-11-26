import { describe, expect, it } from "vitest";

import { buildChatPayload, canSend } from "./utils";

const base = {
  assistant: "tutor" as const,
  mode: "hint" as const,
  message: "  Why?  ",
  conversationId: null,
  lessonId: null,
  exerciseId: "",
  code: "",
  attachCode: false,
};

describe("buildChatPayload", () => {
  it("trims the message and leaves out empty fields", () => {
    expect(buildChatPayload(base)).toEqual({ assistant: "tutor", mode: "hint", message: "Why?" });
  });

  it("includes ids and code only when present and attached", () => {
    const payload = buildChatPayload({
      ...base,
      conversationId: "c1",
      lessonId: "l1",
      exerciseId: "e1",
      code: "print(1)",
      attachCode: true,
    });
    expect(payload).toMatchObject({ conversation_id: "c1", lesson_id: "l1", exercise_id: "e1", code: "print(1)" });
  });

  it("does not send code that is not attached or is blank", () => {
    expect(buildChatPayload({ ...base, code: "print(1)", attachCode: false }).code).toBeUndefined();
    expect(buildChatPayload({ ...base, code: "   ", attachCode: true }).code).toBeUndefined();
  });
});

describe("canSend", () => {
  const ok = { mode: "hint" as const, message: "hi", enabled: true, busy: false };
  it("allows a normal message", () => expect(canSend(ok)).toBe(true));
  it("blocks independent mode, blank messages, busy and disabled states", () => {
    expect(canSend({ ...ok, mode: "independent" })).toBe(false);
    expect(canSend({ ...ok, message: "   " })).toBe(false);
    expect(canSend({ ...ok, busy: true })).toBe(false);
    expect(canSend({ ...ok, enabled: false })).toBe(false);
  });
});
