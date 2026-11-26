import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "../components/Button";
import { ErrorNote, Loading } from "../components/StateMessage";
import { deleteConversation, fetchConversation, fetchConversations } from "../features/ai/api";
import { AssistantPanel } from "../features/ai/AssistantPanel";
import type { ConversationDetail } from "../features/ai/types";

export function AssistantPage() {
  const queryClient = useQueryClient();
  const conversations = useQuery({
    queryKey: ["ai", "conversations"],
    queryFn: ({ signal }) => fetchConversations(signal),
  });
  const [selected, setSelected] = useState<ConversationDetail | null>(null);
  const [panelKey, setPanelKey] = useState(0);

  const open = useMutation({
    mutationFn: (id: string) => fetchConversation(id),
    onSuccess: (detail) => {
      setSelected(detail);
      setPanelKey((key) => key + 1);
    },
  });
  const remove = useMutation({
    mutationFn: (id: string) => deleteConversation(id),
    onSuccess: (_result, id) => {
      if (selected?.id === id) {
        setSelected(null);
        setPanelKey((key) => key + 1);
      }
      void queryClient.invalidateQueries({ queryKey: ["ai", "conversations"] });
    },
  });

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Assistant</p>
      <h1 className="mt-2 font-serif text-3xl">AI development assistant</h1>
      <p className="mt-2 max-w-2xl text-ink-muted">
        Seven assistants and five modes. In Hint mode you get guidance, not answers. Independent mode switches the AI off.
      </p>

      <div className="mt-8 grid gap-10 lg:grid-cols-[16rem_minmax(0,1fr)]">
        <aside aria-label="Past conversations">
          <h2 className="font-mono text-xs uppercase tracking-widest text-ink-muted">Past conversations</h2>
          {conversations.isPending && <Loading label="Loading" />}
          {conversations.isError && <ErrorNote error={conversations.error} />}
          {conversations.data && conversations.data.length === 0 && (
            <p className="mt-2 text-sm text-ink-muted">None yet.</p>
          )}
          {conversations.data && conversations.data.length > 0 && (
            <ul className="mt-2 divide-y divide-rule border-y border-rule text-sm">
              {conversations.data.map((item) => (
                <li key={item.id} className="py-2">
                  <button
                    type="button"
                    onClick={() => open.mutate(item.id)}
                    className={`block w-full text-left hover:text-signal ${selected?.id === item.id ? "text-signal" : ""}`}
                  >
                    {item.title}
                  </button>
                  <span className="font-mono text-xs text-ink-muted">
                    {item.assistant}, {new Date(item.updated_at).toLocaleDateString()}
                  </span>{" "}
                  <Button variant="danger" className="ml-1 px-1.5 py-0 text-xs" onClick={() => remove.mutate(item.id)} disabled={remove.isPending}>
                    Delete
                  </Button>
                </li>
              ))}
            </ul>
          )}
          {open.isError && <ErrorNote error={open.error} />}
          {remove.isError && <ErrorNote error={remove.error} />}
        </aside>

        <section aria-label="Assistant workspace">
          <AssistantPanel key={panelKey} initial={selected} />
        </section>
      </div>
    </div>
  );
}
