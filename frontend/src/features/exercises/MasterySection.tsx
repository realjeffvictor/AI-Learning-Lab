import { useQuery } from "@tanstack/react-query";

import { ErrorNote, Loading } from "../../components/StateMessage";
import { fetchMastery } from "./api";
import { percent } from "./utils";

export function MasterySection() {
  const mastery = useQuery({ queryKey: ["mastery"], queryFn: ({ signal }) => fetchMastery(signal) });

  return (
    <section className="mt-10" aria-labelledby="mastery-heading">
      <h2 id="mastery-heading" className="mb-1 font-mono text-xs uppercase tracking-widest text-ink-muted">
        Exercise results by concept
      </h2>
      <p className="max-w-2xl text-sm text-ink-muted">
        How you scored on graded exercises, using your latest attempt at each one. Code exercise scores are self-reported.
      </p>
      {mastery.isPending && <Loading label="Loading results" />}
      {mastery.isError && <ErrorNote error={mastery.error} />}
      {mastery.data && mastery.data.length === 0 && (
        <p className="mt-3 text-sm text-ink-muted">Submit an exercise and your results will appear here.</p>
      )}
      {mastery.data && mastery.data.length > 0 && (
        <ul className="mt-3 divide-y divide-rule border-y border-rule text-sm">
          {mastery.data.map((item) => {
            const value = percent(item.correct, item.total);
            return (
              <li key={item.slug} className="grid grid-cols-[minmax(0,1fr)_8rem_4rem] items-center gap-3 py-2">
                <span>
                  <span className="mr-2 font-mono text-xs text-ink-muted">{item.category}</span>
                  {item.name}
                </span>
                <span
                  role="img"
                  aria-label={`${value} percent`}
                  className="block h-2 bg-surface-sunk"
                >
                  <span className={`block h-2 ${value >= 70 ? "bg-ok" : "bg-warn"}`} style={{ width: `${value}%` }} />
                </span>
                <span className="text-right font-mono text-xs text-ink-muted">
                  {item.correct}/{item.total}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
