import { useState } from "react";

import { Button } from "../../components/Button";
import { LazyCodeEditor } from "../python/LazyCodeEditor";
import { pythonRunner, type RunResult, type TestRun } from "../python/pythonRunner";
import { RunConsole } from "../python/RunConsole";
import { useRunnerState } from "../python/useRunnerState";
import type { CodeDefinition, ExerciseProps } from "./types";

export function CodeExercise({ exercise, submit, busy }: ExerciseProps) {
  const definition = exercise.definition as unknown as CodeDefinition;
  const [code, setCode] = useState(definition.starter_code);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [testRun, setTestRun] = useState<TestRun | null>(null);
  const state = useRunnerState();
  const working = state === "loading" || state === "running";
  const timeoutMs = definition.timeout_seconds * 1000;

  async function onRun() {
    setRunResult(null);
    setRunResult(await pythonRunner.run(code, timeoutMs));
  }

  async function onSubmit() {
    setTestRun(null);
    const run = await pythonRunner.runTests(code, definition.tests, timeoutMs);
    setTestRun(run);
    // Nothing is submitted when the runtime itself failed, so a download error never costs an attempt.
    if (run.failure || run.results.length !== definition.tests.length) return;
    submit({ code, results: run.results.map((item) => ({ id: item.id, passed: item.passed })) });
  }

  return (
    <div>
      <LazyCodeEditor value={code} onChange={setCode} ariaLabel={`Code for ${exercise.title}`} height="14rem" />
      <div className="mt-3 flex flex-wrap gap-2">
        <Button variant="secondary" onClick={() => void onRun()} disabled={working || busy}>
          Run
        </Button>
        <Button onClick={() => void onSubmit()} disabled={working || busy || !code.trim()}>
          {busy ? "Scoring..." : "Run tests and submit"}
        </Button>
        <Button variant="secondary" onClick={() => pythonRunner.stop()} disabled={state !== "running"}>
          Stop
        </Button>
        <Button variant="secondary" onClick={() => setCode(definition.starter_code)} disabled={working}>
          Reset code
        </Button>
      </div>

      <div className="mt-3">
        <RunConsole result={runResult} state={state} />
      </div>

      {testRun && (
        <div className="mt-3 text-sm">
          {testRun.failure && (
            <p role="alert" className="text-danger">
              {testRun.failure} Nothing was submitted.
            </p>
          )}
          {testRun.error && <pre className="whitespace-pre-wrap font-mono text-xs text-danger">{testRun.error}</pre>}
          {testRun.results.length > 0 && (
            <ul className="mt-2 divide-y divide-rule border-y border-rule">
              {testRun.results.map((item) => {
                const test = definition.tests.find((t) => t.id === item.id);
                return (
                  <li key={item.id} className="py-1">
                    <span className={item.passed ? "text-ok" : "text-danger"}>{item.passed ? "Pass" : "Fail"}</span>{" "}
                    {test?.description}
                    {!item.passed && item.message && (
                      <span className="block font-mono text-xs text-ink-muted">{item.message}</span>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
      <p className="mt-3 text-xs text-ink-muted">
        Code tests run in your browser, so this score is self-reported. Quizzes and puzzles are scored by the server.
      </p>
    </div>
  );
}
