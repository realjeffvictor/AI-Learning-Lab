import type { InputHTMLAttributes } from "react";

interface FieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: string;
}

export function Field({ label, hint, id, ...rest }: FieldProps) {
  const inputId = id ?? rest.name;
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={inputId} className="font-mono text-xs uppercase tracking-widest text-ink-muted">
        {label}
      </label>
      <input
        id={inputId}
        {...rest}
        className="rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink placeholder:text-ink-muted"
      />
      {hint && <p className="text-xs text-ink-muted">{hint}</p>}
    </div>
  );
}
