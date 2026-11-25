import type { ReactNode } from "react";
import { Link } from "react-router-dom";

import { PRINCIPLES } from "../../lib/principles";

interface AuthLayoutProps {
  title: string;
  subtitle: string;
  footer: ReactNode;
  children: ReactNode;
}

export function AuthLayout({ title, subtitle, footer, children }: AuthLayoutProps) {
  return (
    <main className="mx-auto grid min-h-screen max-w-[1200px] gap-12 px-6 py-12 lg:grid-cols-2 lg:items-center lg:gap-24">
      <section className="flex flex-col gap-8">
        <Link to="/" className="font-serif text-2xl">
          AI Learning Lab
        </Link>
        <p className="max-w-md font-serif text-lg text-ink-muted">From Python Foundations to Intelligent Automation.</p>
        <ul aria-label="The five principles" className="max-w-sm divide-y divide-rule border-y border-rule font-mono text-sm">
          {PRINCIPLES.map(([glyph, name]) => (
            <li key={glyph} className="grid grid-cols-[2rem_1fr] gap-2 py-2">
              <span className="text-signal">{glyph}</span>
              <span>{name}</span>
            </li>
          ))}
        </ul>
      </section>
      <section className="max-w-md">
        <h1 className="font-serif text-3xl">{title}</h1>
        <p className="mt-2 text-ink-muted">{subtitle}</p>
        <div className="mt-8">{children}</div>
        <p className="mt-6 text-sm text-ink-muted">{footer}</p>
      </section>
    </main>
  );
}
