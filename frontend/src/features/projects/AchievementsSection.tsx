import { useQuery } from "@tanstack/react-query";

import { ErrorNote, Loading } from "../../components/StateMessage";
import { fetchAchievements } from "./api";

export function AchievementsSection() {
  const achievements = useQuery({ queryKey: ["achievements"], queryFn: ({ signal }) => fetchAchievements(signal) });

  return (
    <section className="mt-10" aria-labelledby="achievements-heading">
      <h2 id="achievements-heading" className="mb-1 font-mono text-xs uppercase tracking-widest text-ink-muted">
        Achievements
      </h2>
      <p className="max-w-2xl text-sm text-ink-muted">
        Awarded from what is recorded on the platform. Project achievements need a reviewer to approve your work.
      </p>
      {achievements.isPending && <Loading label="Loading achievements" />}
      {achievements.isError && <ErrorNote error={achievements.error} />}
      {achievements.data && (
        <ul className="mt-3 divide-y divide-rule border-y border-rule text-sm">
          {achievements.data.map((item) => (
            <li key={item.key} className="grid grid-cols-[1.5rem_minmax(0,1fr)_auto] items-baseline gap-3 py-2">
              <span className={item.earned ? "text-ok" : "text-ink-muted"} aria-hidden="true">
                {item.earned ? "+" : "-"}
              </span>
              <span>
                <span className={item.earned ? "" : "text-ink-muted"}>{item.title}</span>
                <span className="block text-xs text-ink-muted">{item.description}</span>
              </span>
              <span className="font-mono text-xs text-ink-muted">
                {item.earned && item.earned_at ? new Date(item.earned_at).toLocaleDateString() : "locked"}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
