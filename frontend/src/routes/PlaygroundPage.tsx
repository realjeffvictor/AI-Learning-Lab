import { useState } from "react";

import { Button } from "../components/Button";
import { LazyCodeEditor } from "../features/python/LazyCodeEditor";
import { pythonRunner, type RunResult } from "../features/python/pythonRunner";
import { RunConsole } from "../features/python/RunConsole";
import { useRunnerState } from "../features/python/useRunnerState";

const STORAGE_KEY = "ail.playground.code";
const STARTER = `# Python playground. Runs in your browser.
name = "world"
print(f"Hello, {name}")

for number in range(1, 4):
    print(number * number)
`;

function loadDraft(): string {
  try {
    return localStorage.getItem(STORAGE_KEY) ?? STARTER;
  } catch {
    return STARTER;
  }
}

function saveDraft(code: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, code);
  } catch {
    // Storage can be unavailable (private windows); the draft just will not persist.
  }
}

export function PlaygroundPage() {
  const [code, setCode] = useState(loadDraft);
  const [result, setResult] = useState<RunResult | null>(null);
  const state = useRunnerState();
  const working = state === "loading" || state === "running";

  function onChange(next: string) {
    setCode(next);
    saveDraft(next);
  }

  async function onRun() {
    setResult(null);
    setResult(await pythonRunner.run(code));
  }

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Playground</p>
      <h1 className="mt-2 font-serif text-3xl">Python playground</h1>
      <p className="mt-2 max-w-2xl text-ink-muted">
        Write and run Python without installing anything. Your code stays in this browser.
      </p>

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <div>
          <LazyCodeEditor value={code} onChange={onChange} ariaLabel="Python code" height="22rem" />
          <div className="mt-3 flex flex-wrap gap-2">
            <Button onClick={() => void onRun()} disabled={working || !code.trim()}>
              Run
            </Button>
            <Button variant="secondary" onClick={() => pythonRunner.stop()} disabled={state !== "running"}>
              Stop
            </Button>
            <Button variant="secondary" onClick={() => onChange(STARTER)} disabled={working}>
              Reset
            </Button>
            <Button variant="secondary" onClick={() => setResult(null)} disabled={working || !result}>
              Clear output
            </Button>
          </div>
          <div className="mt-3">
            <RunConsole result={result} state={state} />
          </div>
        </div>

        <aside className="text-sm">
          <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Limits of the browser runner</p>
          <ul className="mt-2 list-disc space-y-1 pl-4 text-ink-muted">
            <li>Standard library only. Packages such as NumPy arrive in a later phase.</li>
            <li>No network access and no files outside the sandbox.</li>
            <li>input() is not available.</li>
            <li>Runs stop after 10 seconds, so infinite loops cannot freeze the page.</li>
            <li>The first run downloads about 10 MB, then it is cached by your browser.</li>
            <li>Best on a desktop or laptop. Editing code on a phone works but is awkward.</li>
          </ul>
        </aside>
      </div>
    </div>
  );
}
