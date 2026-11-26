/* Classic Web Worker hosting Pyodide. Student code runs here, never on the server and never on the main thread.
   Protocol: {type:"init", indexURL} -> {type:"ready"} | {type:"init-error", message}
             {type:"run", id, code}  -> {type:"run-result", id, ok, stdout, stderr, error}
             {type:"test", id, code, tests} -> {type:"test-result", id, results, error}
   The client enforces timeouts by terminating this worker. Network APIs are disabled once Python has loaded;
   that is best-effort hardening, not a security boundary. */
"use strict";

let pyodide = null;
let helpers = null;
const MAX_OUTPUT_CHARS = 20000;

const HELPERS_SOURCE = `
import importlib.util
import json
from pyodide.code import find_imports

def find_missing(code):
    try:
        names = find_imports(code)
    except SyntaxError:
        return []
    missing = []
    for name in names:
        try:
            found = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError, AttributeError):
            found = False
        if not found:
            missing.append(name)
    return missing

def check_return(ns, call, expected_json):
    try:
        value = eval(call, ns)
    except BaseException as exc:
        return {"passed": False, "message": f"{type(exc).__name__}: {exc}"}
    try:
        actual = json.loads(json.dumps(value))
    except (TypeError, ValueError):
        return {"passed": False, "message": f"Result {value!r} cannot be compared"}
    expected = json.loads(expected_json)
    ok = actual == expected
    return {"passed": ok, "message": "" if ok else f"Expected {expected!r}, got {actual!r}"}
`;

const BLOCKED = ["fetch", "XMLHttpRequest", "WebSocket", "EventSource", "importScripts", "indexedDB", "caches",
  "BroadcastChannel", "SharedWorker", "Worker", "WebTransport"];

function blockNetwork() {
  const stub = function () { throw new Error("Network access is disabled in the Python sandbox."); };
  let target = self;
  while (target && target !== Object.prototype) {
    for (const name of BLOCKED) {
      if (Object.prototype.hasOwnProperty.call(target, name)) {
        try { Object.defineProperty(target, name, { value: stub, writable: false, configurable: false }); } catch (e) { /* ignore */ }
      }
    }
    target = Object.getPrototypeOf(target);
  }
}

function toJs(value) {
  if (value && typeof value.toJs === "function") {
    const converted = value.toJs({ dict_converter: Object.fromEntries });
    value.destroy();
    return converted;
  }
  return value;
}

async function init(indexURL) {
  importScripts(indexURL + "pyodide.js");
  pyodide = await loadPyodide({ indexURL });
  try { pyodide.setStdin({ stdin: () => null }); } catch (e) { /* input() will raise EOFError either way */ }
  const ns = pyodide.globals.get("dict")();
  pyodide.runPython(HELPERS_SOURCE, { globals: ns });
  helpers = { findMissing: ns.get("find_missing"), checkReturn: ns.get("check_return") };
  blockNetwork();
}

function newNamespace() {
  const ns = pyodide.globals.get("dict")();
  ns.set("__name__", "__main__");
  return ns;
}

function makeCapture() {
  const out = [];
  const err = [];
  let size = 0;
  const push = (list) => (line) => {
    if (size > MAX_OUTPUT_CHARS) return;
    size += line.length + 1;
    list.push(size > MAX_OUTPUT_CHARS ? "[output truncated]" : line);
  };
  pyodide.setStdout({ batched: push(out) });
  pyodide.setStderr({ batched: push(err) });
  return { out, err };
}

function cleanTraceback(message) {
  const lines = String(message).split("\n");
  const start = lines.findIndex((line) => line.includes('File "<exec>"'));
  if (start > 0) return ["Traceback (most recent call last):", ...lines.slice(start)].join("\n").trim();
  return String(message).trim();
}

function missingMessage(names) {
  const list = names.map((n) => '"' + n + '"').join(", ");
  return "Module " + list + " is not available. Only the Python standard library can run in the browser for now.";
}

async function runUser(code, ns) {
  try {
    await pyodide.runPythonAsync(code, { globals: ns });
    return null;
  } catch (e) {
    return cleanTraceback(e && e.message ? e.message : e);
  }
}

async function handleRun(msg) {
  const missing = toJs(helpers.findMissing(msg.code));
  if (missing.length > 0) {
    post({ type: "run-result", id: msg.id, ok: false, stdout: "", stderr: "", error: missingMessage(missing) });
    return;
  }
  const capture = makeCapture();
  const ns = newNamespace();
  const error = await runUser(msg.code, ns);
  ns.destroy();
  post({ type: "run-result", id: msg.id, ok: error === null, stdout: capture.out.join("\n"), stderr: capture.err.join("\n"), error });
}

async function handleTests(msg) {
  const missing = toJs(helpers.findMissing(msg.code));
  if (missing.length > 0) {
    const reason = missingMessage(missing);
    post({ type: "test-result", id: msg.id, error: reason,
      results: msg.tests.map((t) => ({ id: t.id, passed: false, message: reason })) });
    return;
  }

  let loadError = null;
  let shared = null;
  if (msg.tests.some((t) => t.type === "return")) {
    makeCapture();
    shared = newNamespace();
    loadError = await runUser(msg.code, shared);
  }

  const results = [];
  for (const test of msg.tests) {
    if (test.type === "return") {
      if (loadError !== null) {
        results.push({ id: test.id, passed: false, message: "Your code raised an error before this check could run." });
      } else {
        const outcome = toJs(helpers.checkReturn(shared, test.call, JSON.stringify(test.expected)));
        results.push({ id: test.id, passed: Boolean(outcome.passed), message: outcome.message || "" });
      }
    } else {
      const capture = makeCapture();
      const ns = newNamespace();
      const error = await runUser(msg.code, ns);
      ns.destroy();
      const actual = capture.out.join("\n").trimEnd();
      const expected = String(test.expected_stdout).trimEnd();
      const passed = error === null && actual === expected;
      let message = "";
      if (error !== null) message = error.split("\n").slice(-1)[0];
      else if (!passed) message = "Expected output " + JSON.stringify(expected) + ", got " + JSON.stringify(actual);
      results.push({ id: test.id, passed, message });
    }
  }
  if (shared) shared.destroy();
  post({ type: "test-result", id: msg.id, results, error: loadError });
}

function post(message) {
  self.postMessage(message);
}

self.onmessage = async (event) => {
  const msg = event.data;
  try {
    if (msg.type === "init") {
      await init(msg.indexURL);
      post({ type: "ready" });
    } else if (msg.type === "run") {
      await handleRun(msg);
    } else if (msg.type === "test") {
      await handleTests(msg);
    }
  } catch (e) {
    const message = e && e.message ? e.message : String(e);
    if (msg.type === "init") post({ type: "init-error", message });
    else if (msg.type === "test") post({ type: "test-result", id: msg.id, results: [], error: message });
    else post({ type: "run-result", id: msg.id, ok: false, stdout: "", stderr: "", error: message });
  }
};
