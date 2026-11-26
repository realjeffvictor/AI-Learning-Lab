import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { fetchHistory } from "./api";

export function AttemptHistory({ exerciseId, attempts }: { exerciseId: string; attempts: number }) {
  const [open, setOpen] = useState(false);
  const history = useQuery({
    queryKey: ["history", exerciseId],
    queryFn: ({ signal }) => fetchHistory(exerciseId, signal),
    enabled: open && attempts > 0,
  });

  if (attempts === 0) return null;
  return (
    <details className="mt-4 text-sm" onToggle={(event) => setOpen(event.currentTarget.open)}>
      <summary className="cursor-pointer font-mono text-xs uppercase tracking-widest text-ink-muted">
        Attempt history ({attempts})
      </summary>
      {history.isPending && <p className="mt-2 text-ink-muted">Loading...</p>}
      {history.data && (
        <ul className="mt-2 divide-y divide-rule border-y border-rule font-mono text-xs">
          {history.data.map((item) => (
            <li key={item.id} className="grid grid-cols-[1fr_4rem_5rem] gap-3 py-1">
              <span className="text-ink-muted">{new Date(item.created_at).toLocaleString()}</span>
              <span>{item.score}/100</span>
              <span className={item.passed ? "text-ok" : "text-warn"}>{item.passed ? "passed" : "not passed"}</span>
            </li>
          ))}
        </ul>
      )}
    </details>
  );
}
