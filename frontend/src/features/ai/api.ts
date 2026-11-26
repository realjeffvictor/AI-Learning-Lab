import { authedRequest } from "../auth/session";
import type { AIStatus, ChatPayload, ChatResponse, ConversationDetail, ConversationSummary, StudyPlan } from "./types";

const enc = encodeURIComponent;

export const fetchAIStatus = (signal?: AbortSignal) => authedRequest<AIStatus>("/api/v1/ai/status", { signal });

export const sendChat = (payload: ChatPayload) =>
  authedRequest<ChatResponse>("/api/v1/ai/chat", { method: "POST", body: payload });

export const requestStudyPlan = () => authedRequest<StudyPlan>("/api/v1/ai/study-plan", { method: "POST" });

export const fetchConversations = (signal?: AbortSignal) =>
  authedRequest<ConversationSummary[]>("/api/v1/ai/conversations", { signal });

export const fetchConversation = (id: string, signal?: AbortSignal) =>
  authedRequest<ConversationDetail>(`/api/v1/ai/conversations/${enc(id)}`, { signal });

export const deleteConversation = (id: string) =>
  authedRequest<void>(`/api/v1/ai/conversations/${enc(id)}`, { method: "DELETE" });
