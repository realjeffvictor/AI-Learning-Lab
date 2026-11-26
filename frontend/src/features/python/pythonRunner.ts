import { PYODIDE_VERSION } from "./pyodideVersion";

export type RunnerState = "idle" | "loading" | "ready" | "running";
export type Interruption = "timeout" | "stopped" | null;

export interface CodeTest {
  id: string;
  description: string;
  type: "return" | "stdout";
  call?: string;
  expected?: unknown;
  expected_stdout?: string;
}

export interface RunResult {
  ok: boolean;
  stdout: string;
  stderr: string;
  error: string | null;
  interrupted: Interruption;
}

export interface TestResult {
  id: string;
  passed: boolean;
  message: string;
}

export interface TestRun {
  results: TestResult[];
  /** Error raised by the learner's code while loading it, if any. */
  error: string | null;
  /** Set when the runtime itself could not run (download failed, worker crashed). Nothing should be submitted. */
  failure: string | null;
  interrupted: Interruption;
}

interface Outcome {
  reply: Record<string, unknown> | null;
  interrupted: Interruption;
  failure: string | null;
}

const INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
const LOAD_TIMEOUT_MS = 90_000;
export const DEFAULT_TIMEOUT_MS = 10_000;

function interruptionMessage(kind: Exclude<Interruption, null>, timeoutMs: number): string {
  return kind === "timeout"
    ? `Stopped: your code ran for more than ${Math.round(timeoutMs / 1000)} seconds. Check for an infinite loop.`
    : "Stopped.";
}

/** One shared Python worker. Runs are serialised; a timeout or Stop terminates the worker and the next run starts a new one. */
class PythonRunner {
  private worker: Worker | null = null;
  private ready: Promise<Worker> | null = null;
  private state: RunnerState = "idle";
  private listeners = new Set<() => void>();
  private busy = false;
  private counter = 0;
  private cancel: (() => void) | null = null;

  subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };

  getState = (): RunnerState => this.state;

  private setState(state: RunnerState): void {
    if (this.state === state) return;
    this.state = state;
    this.listeners.forEach((listener) => listener());
  }

  private kill(): void {
    this.worker?.terminate();
    this.worker = null;
    this.ready = null;
  }

  private start(): Promise<Worker> {
    if (this.ready) return this.ready;
    const worker = new Worker("/pyodide-worker.js");
    this.worker = worker;
    this.ready = new Promise<Worker>((resolve, reject) => {
      const fail = (message: string) => {
        window.clearTimeout(timer);
        worker.terminate();
        if (this.worker === worker) {
          this.worker = null;
          this.ready = null;
        }
        reject(new Error(message));
      };
      const timer = window.setTimeout(
        () => fail("Python took too long to load. Check your internet connection and try again."),
        LOAD_TIMEOUT_MS,
      );
      worker.onmessage = (event: MessageEvent<{ type: string; message?: string }>) => {
        if (event.data.type === "ready") {
          window.clearTimeout(timer);
          resolve(worker);
        } else if (event.data.type === "init-error") {
          fail(`Python could not start: ${event.data.message ?? "unknown error"}. Check your internet connection.`);
        }
      };
      worker.onerror = (event) => fail(event.message || "The Python worker failed to start.");
      worker.postMessage({ type: "init", indexURL: INDEX_URL });
    });
    return this.ready;
  }

  private async request(message: Record<string, unknown>, timeoutMs: number): Promise<Outcome> {
    if (this.busy) return { reply: null, interrupted: null, failure: "Another run is still in progress." };
    this.busy = true;
    try {
      if (!this.worker) this.setState("loading");
      let worker: Worker;
      try {
        worker = await this.start();
      } catch (error) {
        this.setState("idle");
        return { reply: null, interrupted: null, failure: error instanceof Error ? error.message : String(error) };
      }
      this.setState("running");
      const id = ++this.counter;
      return await new Promise<Outcome>((resolve) => {
        const finish = (outcome: Outcome) => {
          window.clearTimeout(timer);
          this.cancel = null;
          resolve(outcome);
        };
        const timer = window.setTimeout(() => {
          this.kill();
          finish({ reply: null, interrupted: "timeout", failure: null });
        }, timeoutMs);
        this.cancel = () => {
          this.kill();
          finish({ reply: null, interrupted: "stopped", failure: null });
        };
        worker.onmessage = (event: MessageEvent<Record<string, unknown>>) => {
          if (event.data.id === id) finish({ reply: event.data, interrupted: null, failure: null });
        };
        worker.onerror = (event) => {
          this.kill();
          finish({ reply: null, interrupted: null, failure: event.message || "The Python worker crashed." });
        };
        worker.postMessage({ ...message, id });
      });
    } finally {
      this.busy = false;
      this.setState(this.worker ? "ready" : "idle");
    }
  }

  /** Stop the current run (terminates the worker; the next run reloads it from the browser cache). */
  stop(): void {
    this.cancel?.();
  }

  async run(code: string, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<RunResult> {
    const outcome = await this.request({ type: "run", code }, timeoutMs);
    const stopped = { ok: false, stdout: "", stderr: "", interrupted: outcome.interrupted };
    if (outcome.interrupted) return { ...stopped, error: interruptionMessage(outcome.interrupted, timeoutMs) };
    if (outcome.failure || !outcome.reply) return { ...stopped, error: outcome.failure ?? "No result." };
    const reply = outcome.reply;
    return {
      ok: Boolean(reply.ok),
      stdout: String(reply.stdout ?? ""),
      stderr: String(reply.stderr ?? ""),
      error: typeof reply.error === "string" ? reply.error : null,
      interrupted: null,
    };
  }

  async runTests(code: string, tests: CodeTest[], timeoutMs = DEFAULT_TIMEOUT_MS): Promise<TestRun> {
    const outcome = await this.request({ type: "test", code, tests }, timeoutMs);
    if (outcome.interrupted) {
      return { results: [], error: null, failure: interruptionMessage(outcome.interrupted, timeoutMs), interrupted: outcome.interrupted };
    }
    if (outcome.failure || !outcome.reply) {
      return { results: [], error: null, failure: outcome.failure ?? "No result.", interrupted: null };
    }
    const reply = outcome.reply;
    return {
      results: Array.isArray(reply.results) ? (reply.results as TestResult[]) : [],
      error: typeof reply.error === "string" ? reply.error : null,
      failure: null,
      interrupted: null,
    };
  }
}

export const pythonRunner = new PythonRunner();
