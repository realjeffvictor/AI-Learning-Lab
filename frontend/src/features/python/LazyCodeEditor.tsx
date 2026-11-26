import { lazy, Suspense } from "react";

const CodeEditor = lazy(() => import("./CodeEditor"));

interface LazyCodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  height?: string;
  ariaLabel: string;
}

/** Monaco is only downloaded on pages that show an editor. */
export function LazyCodeEditor(props: LazyCodeEditorProps) {
  return (
    <Suspense fallback={<p className="border border-rule p-3 font-mono text-sm text-ink-muted">Loading editor...</p>}>
      <CodeEditor {...props} />
    </Suspense>
  );
}
