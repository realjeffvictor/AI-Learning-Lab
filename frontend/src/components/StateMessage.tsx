import { describeError } from "../lib/api/messages";

export function Loading({ label }: { label: string }) {
  return (
    <p role="status" className="font-mono text-sm text-ink-muted">
      {label}...
    </p>
  );
}

export function ErrorNote({ error }: { error: unknown }) {
  return (
    <p role="alert" className="text-sm text-danger">
      {describeError(error)}
    </p>
  );
}
