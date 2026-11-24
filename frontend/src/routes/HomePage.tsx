import { StatusPanel } from "../features/health/StatusPanel";

const PRINCIPLES = [
  ["U", "Understand"],
  ["D", "Direct"],
  ["B", "Build"],
  ["V", "Verify"],
  ["O", "Own"],
] as const;

export function HomePage() {
  return (
    <main className="mx-auto grid min-h-screen max-w-[1200px] gap-12 px-6 py-12 lg:grid-cols-[minmax(0,1fr)_26rem] lg:gap-20 lg:py-24">
      <header className="flex flex-col gap-10">
        <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Phase 1 / Foundation</p>
        <div>
          <h1 className="font-serif text-4xl leading-tight">AI Learning Lab</h1>
          <p className="mt-3 max-w-xl font-serif text-lg text-ink-muted">
            From Python Foundations to Intelligent Automation.
          </p>
        </div>
        <ul aria-label="The five principles" className="max-w-xl divide-y divide-rule border-y border-rule font-mono text-sm">
          {PRINCIPLES.map(([glyph, name]) => (
            <li key={glyph} className="grid grid-cols-[2rem_1fr] gap-2 py-2">
              <span className="text-signal">{glyph}</span>
              <span>{name}</span>
            </li>
          ))}
        </ul>
      </header>
      <StatusPanel />
    </main>
  );
}
