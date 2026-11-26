import type { Recommendation } from "../exercises/types";

export type AssistantId = "tutor" | "code" | "debug" | "architecture" | "testing" | "docs" | "review";
export type ModeId = "independent" | "hint" | "pair" | "generate" | "review";

export interface AssistantInfo {
  id: AssistantId;
  label: string;
  blurb: string;
}
export interface ModeInfo {
  id: ModeId;
  label: string;
  blurb: string;
}

export const ASSISTANTS: AssistantInfo[] = [
  { id: "tutor", label: "Tutor", blurb: "Explains the lesson and checks your understanding." },
  { id: "code", label: "Code", blurb: "Helps write and explain Python." },
  { id: "debug", label: "Debug", blurb: "Walks you through finding the root cause of an error." },
  { id: "architecture", label: "Architecture", blurb: "Discusses structure and trade-offs." },
  { id: "testing", label: "Testing", blurb: "Suggests test cases and explains what they prove." },
  { id: "docs", label: "Documentation", blurb: "Drafts docstrings and README text." },
  { id: "review", label: "Code review", blurb: "Points out problems without rewriting your code." },
];

export const MODES: ModeInfo[] = [
  { id: "independent", label: "Independent", blurb: "AI is off. You work on your own." },
  { id: "hint", label: "Hint", blurb: "Guidance without the answer." },
  { id: "pair", label: "Pair programming", blurb: "Works alongside you and explains each step." },
  { id: "generate", label: "Generate and explain", blurb: "Writes code and explains how it works." },
  { id: "review", label: "Code review", blurb: "Finds problems and leaves the fixing to you." },
];

export interface Usage {
  requests_used: number;
  requests_limit: number;
  tokens_used: number;
  tokens_limit: number;
}
export interface AIStatus {
  enabled: boolean;
  model: string | null;
  usage: Usage;
}
export interface ChatPayload {
  assistant: AssistantId;
  mode: ModeId;
  message: string;
  conversation_id?: string;
  lesson_id?: string;
  exercise_id?: string;
  code?: string;
}
export interface ChatResponse {
  conversation_id: string;
  assistant: AssistantId;
  mode: Exclude<ModeId, "independent">;
  reply: string;
  usage: Usage;
}
export interface ConversationSummary {
  id: string;
  assistant: AssistantId;
  title: string;
  updated_at: string;
}
export interface StoredMessage {
  id: string;
  role: "user" | "assistant";
  mode: string;
  content: string;
  created_at: string;
}
export interface ConversationDetail {
  id: string;
  assistant: AssistantId;
  title: string;
  messages: StoredMessage[];
}
export interface StudyPlan {
  reply: string;
  weak_concepts: { slug: string; name: string; correct: number; total: number }[];
  recommendations: Recommendation[];
  usage: Usage;
}
