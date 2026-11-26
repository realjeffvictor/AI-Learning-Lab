import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "../components/Button";
import { ErrorNote, Loading } from "../components/StateMessage";
import { fetchQueue } from "../features/projects/api";
import { KIND_LABEL } from "../features/projects/utils";

const PAGE_SIZE = 20;

export function ReviewQueuePage() {
  const [page, setPage] = useState(1);
  const queue = useQuery({
    queryKey: ["reviews", "queue", page],
    queryFn: ({ signal }) => fetchQueue(page, PAGE_SIZE, signal),
    placeholderData: keepPreviousData,
  });

  if (queue.isPending) return <Loading label="Loading review queue" />;
  if (queue.isError) return <ErrorNote error={queue.error} />;
  const totalPages = Math.max(1, Math.ceil(queue.data.total / queue.data.page_size));

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Reviews</p>
      <h1 className="mt-2 font-serif text-3xl">Submissions awaiting review</h1>
      <p className="mt-2 max-w-2xl text-ink-muted">Oldest first. You cannot review your own submissions.</p>

      {queue.data.items.length === 0 ? (
        <p className="mt-8 text-ink-muted">Nothing is waiting for review.</p>
      ) : (
        <ul className="mt-8 divide-y divide-rule border-y border-rule">
          {queue.data.items.map((item) => (
            <li key={item.submission_id} className="grid gap-2 py-3 md:grid-cols-[7rem_minmax(0,1fr)_14rem] md:gap-6">
              <span className="font-mono text-xs uppercase tracking-widest text-signal">{KIND_LABEL[item.project_kind]}</span>
              <div>
                <Link to={`/reviews/${item.submission_id}`} className="font-serif text-lg hover:text-signal">
                  {item.project_title}
                </Link>
                <p className="font-mono text-xs text-ink-muted">
                  {item.learner_name} ({item.learner_email})
                </p>
              </div>
              <span className="font-mono text-xs text-ink-muted">
                Submitted {new Date(item.submitted_at).toLocaleString()}
              </span>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-4 flex items-center gap-3 text-sm">
        <Button variant="secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>
          Previous
        </Button>
        <span className="font-mono text-ink-muted">
          {page} / {totalPages}
        </span>
        <Button variant="secondary" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
          Next
        </Button>
        <span className="ml-auto text-ink-muted">{queue.data.total} waiting</span>
      </div>
    </div>
  );
}
