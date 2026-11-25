import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "danger";

const STYLES: Record<Variant, string> = {
  primary: "bg-signal text-signal-ink hover:opacity-90",
  secondary: "border border-rule bg-surface text-ink hover:border-ink-muted",
  danger: "border border-danger text-danger hover:bg-danger hover:text-paper",
};

export function Button({
  variant = "primary",
  className = "",
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      type="button"
      {...rest}
      className={`rounded-md px-3 py-1.5 text-sm font-medium transition-opacity disabled:opacity-50 ${STYLES[variant]} ${className}`}
    />
  );
}
