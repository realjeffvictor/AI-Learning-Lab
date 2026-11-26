import type { AssistantId, ChatPayload, ModeId } from "./types";

export interface ChatInput {
  assistant: AssistantId;
  mode: ModeId;
  message: string;
  conversationId: string | null;
  lessonId: string | null;
  exerciseId: string;
  code: string;
  attachCode: boolean;
}

/** Builds the request body, leaving out anything that is empty. */
export function buildChatPayload(input: ChatInput): ChatPayload {
  const payload: ChatPayload = { assistant: input.assistant, mode: input.mode, message: input.message.trim() };
  if (input.conversationId) payload.conversation_id = input.conversationId;
  if (input.lessonId) payload.lesson_id = input.lessonId;
  if (input.exerciseId) payload.exercise_id = input.exerciseId;
  if (input.attachCode && input.code.trim()) payload.code = input.code;
  return payload;
}

/** The server enforces all of this too; this only keeps the button honest. */
export function canSend(options: { mode: ModeId; message: string; enabled: boolean; busy: boolean }): boolean {
  return options.enabled && !options.busy && options.mode !== "independent" && options.message.trim().length > 0;
}
