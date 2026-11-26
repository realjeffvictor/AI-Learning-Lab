import Editor, { loader, type BeforeMount } from "@monaco-editor/react";
import { useEffect, useState } from "react";

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  height?: string;
  ariaLabel: string;
}

function token(name: string, fallback: string): string {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return /^#[0-9a-fA-F]{6}$/.test(value) ? value : fallback;
}

function isDark(): boolean {
  const forced = document.documentElement.getAttribute("data-theme");
  if (forced) return forced === "dark";
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

/** Monaco theme derived from the design tokens, so the editor matches the rest of the app. */
const defineLabTheme: BeforeMount = (monaco) => {
  const dark = isDark();
  monaco.editor.defineTheme("lab", {
    base: dark ? "vs-dark" : "vs",
    inherit: true,
    rules: [],
    colors: {
      "editor.background": token("--surface-sunk", dark ? "#100f0c" : "#ece8de"),
      "editor.foreground": token("--ink", dark ? "#ece8dc" : "#1c1b17"),
      "editorLineNumber.foreground": token("--ink-muted", "#5e5a4f"),
      "editorCursor.foreground": token("--signal", "#d9480f"),
      "editor.lineHighlightBackground": token("--surface", dark ? "#1b1a16" : "#ffffff"),
    },
  });
};

export default function CodeEditor({ value, onChange, height = "18rem", ariaLabel }: CodeEditorProps) {
  const [failed, setFailed] = useState(false);

  // Monaco loads from a CDN. If that fails (offline), fall back to a plain text box so the page still works.
  useEffect(() => {
    loader.init().catch(() => setFailed(true));
  }, []);

  if (failed) {
    return (
      <textarea
        aria-label={ariaLabel}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        spellCheck={false}
        style={{ height }}
        className="w-full border border-rule bg-surface-sunk p-3 font-mono text-sm text-ink"
      />
    );
  }

  return (
    <div className="border border-rule" style={{ height }}>
      <Editor
        language="python"
        theme="lab"
        value={value}
        beforeMount={defineLabTheme}
        onChange={(next) => onChange(next ?? "")}
        loading={<p className="p-3 font-mono text-sm text-ink-muted">Loading editor...</p>}
        options={{
          minimap: { enabled: false },
          fontFamily: '"JetBrains Mono Variable", ui-monospace, monospace',
          fontSize: 14,
          tabSize: 4,
          insertSpaces: true,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          ariaLabel,
        }}
      />
    </div>
  );
}
