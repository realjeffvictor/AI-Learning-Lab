import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";

import { Button } from "../../components/Button";
import { ErrorNote } from "../../components/StateMessage";
import { LessonMarkdown } from "../curriculum/LessonMarkdown";
import { fetchAIStatus, sendChat } from "./api";
import {
  ASSISTANTS,
  MODES,
  type AIStatus,
  type AssistantId,
  type ChatPayload,
  type ConversationDetail,
  type ModeId,
} from "./types";
import { buildChatPayload, canSend } from "./utils";

interface Turn {
  role: "user" | "assistant";
  content: string;
}

interface AssistantPanelProps {
  lessonId?: string | null;
  exercises?: { id: string; title: string }[];
  initial?: ConversationDetail | null;
}

export function AssistantPanel({ lessonId = null, exercises = [], initial = null }: AssistantPanelProps) {
  const queryClient = useQueryClient();
  const status = useQuery({ queryKey: ["ai", "status"], queryFn: ({ signal }) => fetchAIStatus(signal) });

  const [assistant, setAssistant] = useState<AssistantId>(initial?.assistant ?? "tutor");
  const [mode, setMode] = useState<ModeId>("hint");
  const [message, setMessage] = useState("");
  const [code, setCode] = useState("");
  const [attachCode, setAttachCode] = useState(false);
  const [exerciseId, setExerciseId] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(initial?.id ?? null);
  const [turns, setTurns] = useState<Turn[]>(
    initial ? initial.messages.map((item) => ({ role: item.role, content: item.content })) : [],
  );

  const send = useMutation({
    mutationFn: (payload: ChatPayload) => sendChat(payload),
    onSuccess: (response, payload) => {
      setConversationId(response.conversation_id);
      setTurns((previous) => [
        ...previous,
        { role: "user", content: payload.message },
        { role: "assistant", content: response.reply },
      ]);
      setMessage("");
      queryClient.setQueryData(["ai", "status"], (old: AIStatus | undefined) =>
        old ? { ...old, usage: response.usage } : old,
      );
      void queryClient.invalidateQueries({ queryKey: ["ai", "conversations"] });
    },
  });

  const enabled = status.data?.enabled ?? false;
  const assistantInfo = ASSISTANTS.find((item) => item.id === assistant);
  const modeInfo = MODES.find((item) => item.id === mode);
  const reviewAssistant = assistant === "review";
  const sendable = canSend({ mode, message, enabled, busy: send.isPending });

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!sendable) return;
    send.mutate(buildChatPayload({ assistant, mode, message, conversationId, lessonId, exerciseId, code, attachCode }));
  }

  function newConversation() {
    setConversationId(null);
    setTurns([]);
    send.reset();
  }

  return (
    <div>
      {status.data && !status.data.enabled && (
        <p role="status" className="mb-4 border border-dashed border-ink-muted p-3 text-sm text-ink-muted">
          The AI assistants are switched off because no API key is configured on the server. Run
          ./scripts/set_openai_key.sh and restart the API.
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="flex flex-col gap-1">
          <label htmlFor="assistant" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
            Assistant
          </label>
          <select
            id="assistant"
            value={assistant}
            disabled={conversationId !== null}
            onChange={(event) => setAssistant(event.target.value as AssistantId)}
            className="rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink disabled:opacity-60"
          >
            {ASSISTANTS.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-ink-muted">{assistantInfo?.blurb}</p>
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="mode" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
            Assistance mode
          </label>
          <select
            id="mode"
            value={mode}
            onChange={(event) => setMode(event.target.value as ModeId)}
            className="rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink"
          >
            {MODES.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-ink-muted">
            {reviewAssistant && mode !== "independent"
              ? "The code reviewer always works in review mode."
              : modeInfo?.blurb}
          </p>
        </div>
      </div>

      {exercises.length > 0 && (
        <div className="mt-4 flex flex-col gap-1">
          <label htmlFor="exercise" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
            About
          </label>
          <select
            id="exercise"
            value={exerciseId}
            onChange={(event) => setExerciseId(event.target.value)}
            className="rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink"
          >
            <option value="">This lesson</option>
            {exercises.map((item) => (
              <option key={item.id} value={item.id}>
                Exercise: {item.title}
              </option>
            ))}
          </select>
          <p className="text-xs text-ink-muted">The AI never sees answer keys, only the exercise instructions.</p>
        </div>
      )}

      {turns.length > 0 && (
        <ol aria-label="Conversation" className="mt-6 space-y-4">
          {turns.map((turn, index) => (
            <li key={index} className={turn.role === "user" ? "border-l-2 border-rule pl-3" : "border-l-2 border-signal pl-3"}>
              <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">
                {turn.role === "user" ? "You" : "AI"}
              </p>
              {turn.role === "user" ? (
                <p className="mt-1 whitespace-pre-wrap">{turn.content}</p>
              ) : (
                <LessonMarkdown source={turn.content} />
              )}
            </li>
          ))}
        </ol>
      )}

      <form onSubmit={onSubmit} className="mt-6 flex flex-col gap-3">
        <label htmlFor="message" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
          Your message
        </label>
        <textarea
          id="message"
          rows={3}
          maxLength={4000}
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          disabled={mode === "independent"}
          placeholder={mode === "independent" ? "AI is off in Independent mode." : "Ask a question or describe the problem"}
          className="rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink disabled:opacity-60"
        />
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={attachCode} onChange={(event) => setAttachCode(event.target.checked)} />
          Attach code (sent to the AI provider, not stored)
        </label>
        {attachCode && (
          <textarea
            aria-label="Code to attach"
            rows={8}
            maxLength={8000}
            spellCheck={false}
            value={code}
            onChange={(event) => setCode(event.target.value)}
            className="border border-rule bg-surface-sunk p-3 font-mono text-sm text-ink"
          />
        )}
        <div className="flex flex-wrap items-center gap-3">
          <Button type="submit" disabled={!sendable}>
            {send.isPending ? "Thinking..." : "Send"}
          </Button>
          {conversationId && (
            <Button variant="secondary" onClick={newConversation} disabled={send.isPending}>
              New conversation
            </Button>
          )}
          {status.data && (
            <span className="ml-auto font-mono text-xs text-ink-muted">
              Today: {status.data.usage.requests_used}/{status.data.usage.requests_limit} requests
            </span>
          )}
        </div>
        {send.isError && <ErrorNote error={send.error} />}
      </form>
      <p className="mt-3 text-xs text-ink-muted">
        AI can be wrong. Verify anything it tells you by running or testing it. That is the V in the five principles.
      </p>
    </div>
  );
}
