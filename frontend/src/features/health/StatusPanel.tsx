import { ApiError } from "../../lib/api/errors";
import { useHealth } from "./useHealth";

type Tone = "ok" | "danger" | "muted";

interface Row {
  label: string;
  value: string;
  tone: Tone;
}

const TONE_CLASS: Record<Tone, string> = {
  ok: "text-ok",
  danger: "text-danger",
  muted: "text-ink-muted",
};

export function StatusPanel() {
  const { data, error, isPending, isFetching, refetch } = useHealth();

  const apiError = error instanceof ApiError ? error : null;
  const apiState = isPending ? "checking" : data ? "reachable" : "unreachable";

  const rows: Row[] = [
    { label: "Frontend", value: import.meta.env.MODE, tone: "ok" },
    { label: "API", value: apiState, tone: data ? "ok" : isPending ? "muted" : "danger" },
    { label: "API version", value: data?.health.version ?? "none", tone: "muted" },
    { label: "Environment", value: data?.health.environment ?? "none", tone: "muted" },
    { label: "Round trip", value: data ? `${data.latencyMs} ms` : "none", tone: "muted" },
  ];

  return (
    <section aria-labelledby="foundation-check" className="font-mono text-sm">
      <h2 id="foundation-check" className="mb-3 text-xs uppercase tracking-widest text-ink-muted">
        Foundation check
      </h2>

      <ol className="divide-y divide-rule border-y border-rule">
        {rows.map((row, index) => (
          <li key={row.label} className="grid grid-cols-[2rem_1fr_auto] items-baseline gap-2 py-2">
            <span className="text-ink-muted">{String(index + 1).padStart(2, "0")}</span>
            <span>{row.label}</span>
            <span className={TONE_CLASS[row.tone]}>{row.value}</span>
          </li>
        ))}
      </ol>

      {error && (
        <div role="alert" className="mt-4 rounded-md border border-danger p-3 text-danger">
          <p>{apiError ? apiError.message : "Unexpected error."}</p>
          {apiError?.requestId && <p className="mt-1 text-xs">request {apiError.requestId}</p>}
          <p className="mt-2 text-xs text-ink-muted">Start the API with ./scripts/dev.sh, then re-check.</p>
        </div>
      )}

      <button
        type="button"
        onClick={() => void refetch()}
        disabled={isFetching}
        className="mt-4 rounded-md bg-signal px-3 py-1.5 text-signal-ink transition-opacity hover:opacity-90 disabled:opacity-50"
      >
        {isFetching ? "Checking..." : "Re-check"}
      </button>
    </section>
  );
}
