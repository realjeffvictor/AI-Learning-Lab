import type { RunnerState, RunResult } from "./pythonRunner";

export function RunConsole({ result, state }: { result: RunResult | null; state: RunnerState }) {
  const busy = state === "loading" || state === "running";
  return (
    <div role="log" aria-live="polite" aria-label="Program output" className="min-h-[7rem] border border-rule bg-surface-sunk p-3 font-mono text-sm">
      {state === "loading" && (
        <p className="text-ink-muted">Loading Python. The first run downloads the runtime (about 10 MB)...</p>
      )}
      {state === "running" && <p className="text-ink-muted">Running...</p>}
      {!busy && !result && <p className="text-ink-muted">Output appears here.</p>}
      {!busy && result && (
        <>
          {result.stdout && <pre className="whitespace-pre-wrap">{result.stdout}</pre>}
          {result.stderr && <pre className="whitespace-pre-wrap text-warn">{result.stderr}</pre>}
          {result.error && <pre className="whitespace-pre-wrap text-danger">{result.error}</pre>}
          {result.ok && !result.stdout && !result.stderr && <p className="text-ink-muted">Finished with no output.</p>}
        </>
      )}
    </div>
  );
}
