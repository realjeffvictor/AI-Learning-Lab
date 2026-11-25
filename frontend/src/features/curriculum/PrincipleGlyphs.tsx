import { PRINCIPLES } from "../../lib/principles";

const NAMES: Record<string, string> = Object.fromEntries(PRINCIPLES);

export function PrincipleGlyphs({ principles }: { principles: string[] }) {
  if (principles.length === 0) return null;
  const names = principles.map((letter) => NAMES[letter] ?? letter).join(", ");
  return (
    <span aria-label={`Principles: ${names}`} title={names} className="font-mono text-xs tracking-widest text-signal">
      {principles.join(" ")}
    </span>
  );
}
