import { Link } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";
import { StatusPanel } from "../features/health/StatusPanel";
import { PRINCIPLES } from "../lib/principles";

export function HomePage() {
  const { status } = useAuth();
  return (
    <main className="mx-auto grid min-h-screen max-w-[1200px] gap-12 px-6 py-12 lg:grid-cols-[minmax(0,1fr)_26rem] lg:gap-20 lg:py-24">
      <header className="flex flex-col gap-10">
        <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Phase 2 / Authentication</p>
        <div>
          <h1 className="font-serif text-4xl leading-tight">AI Learning Lab</h1>
          <p className="mt-3 max-w-xl font-serif text-lg text-ink-muted">
            From Python Foundations to Intelligent Automation.
          </p>
        </div>
        {status === "authenticated" && (
          <div>
            <Link to="/dashboard" className="rounded-md bg-signal px-3 py-1.5 text-sm font-medium text-signal-ink">
              Open dashboard
            </Link>
          </div>
        )}
        {status === "anonymous" && (
          <div className="flex gap-3">
            <Link to="/register" className="rounded-md bg-signal px-3 py-1.5 text-sm font-medium text-signal-ink">
              Create account
            </Link>
            <Link to="/login" className="rounded-md border border-rule px-3 py-1.5 text-sm font-medium">
              Sign in
            </Link>
          </div>
        )}
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
