import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";

type Pillar = "Understand" | "Direct" | "Build" | "Verify" | "Own";

const PILLARS: Pillar[] = ["Understand", "Direct", "Build", "Verify", "Own"];

interface SignInLayoutProps {
  title: string;
  subtitle: string;
  footer: ReactNode;
  children: ReactNode;
}

function PillarIcon({ name }: { name: Pillar }) {
  const common = {
    className: "h-full w-full",
    fill: "none",
    stroke: "currentColor",
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    strokeWidth: 1.8,
  };

  switch (name) {
    case "Understand":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>
          <path d="M12 7c-2.1-2-5.3-2.4-8-1.6v12c2.8-.8 5.9-.4 8 1.6m0-12c2.1-2 5.3-2.4 8-1.6v12c-2.8-.8-5.9-.4-8 1.6m0-12v12" />
          <path d="M12 2.5v1m-6-1 .6 1m10.8-1-.6 1" />
        </svg>
      );
    case "Direct":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>
          <circle cx="12" cy="12" r="9" />
          <path d="m15.8 8.2-2.4 5.2-5.2 2.4 2.4-5.2 5.2-2.4Z" />
          <circle cx="12" cy="12" r=".7" fill="currentColor" stroke="none" />
        </svg>
      );
    case "Build":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>
          <path d="m8 7-5 5 5 5m8-10 5 5-5 5m-2-12-4 14" />
        </svg>
      );
    case "Verify":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>
          <path d="M12 3 20 6v5c0 5-3.4 8.3-8 10-4.6-1.7-8-5-8-10V6l8-3Z" />
          <path d="m8.5 12 2.3 2.3 4.8-5" />
        </svg>
      );
    case "Own":
      return (
        <svg viewBox="0 0 24 24" aria-hidden="true" {...common}>
          <path d="M5 15.5c2-5.7 7-9.8 15-10.5-.7 8-4.8 13-10.5 15L5 15.5Z" />
          <path d="m5 15.5-2 5.5 5.5-2m6.2-8.8a1.8 1.8 0 1 0 0 3.6 1.8 1.8 0 0 0 0-3.6Z" />
          <path d="M6 9 4 7m3-3-1-2m-2 8-2-.5" />
        </svg>
      );
  }
}

function CursorIcon() {
  return (
    <svg viewBox="0 0 20 24" className="absolute right-3 top-1/2 h-6 w-5 -translate-y-1/2" aria-hidden="true">
      <path d="M2 1.5v17l4.6-4.1 3.3 7 3.1-1.5-3.3-6.8h6.1L2 1.5Z" fill="white" stroke="#121622" strokeLinejoin="round" strokeWidth="1.5" />
    </svg>
  );
}

export function SignInLayout({ title, subtitle, footer, children }: SignInLayoutProps) {
  const [activePillar, setActivePillar] = useState<Pillar>("Direct");

  return (
    <main className="grid min-h-screen bg-[#FAFAFA] lg:grid-cols-[55fr_45fr]">
      <section className="relative flex min-h-[560px] flex-col overflow-hidden bg-[#121622] px-7 py-10 text-white sm:px-12 sm:py-12 lg:min-h-screen lg:px-[clamp(3rem,6vw,6rem)] lg:py-14">
        <Link to="/" className="flex w-fit items-center gap-4 rounded-sm text-white no-underline">
          <svg viewBox="0 0 48 40" className="h-10 w-12 shrink-0 text-[#E06346]" fill="currentColor" aria-hidden="true">
            <path d="M24 2 1 13l23 11 18-8.6V29h4V13L24 2Zm-15 17v9c0 5 7 9 15 9s15-4 15-9v-9l-15 7-15-7Z" />
            <circle cx="44" cy="31" r="3" />
          </svg>
          <span>
            <span className="block text-[26px] font-semibold leading-tight tracking-[-0.03em]">AI Learning Lab</span>
            <span className="mt-1 block text-sm text-[#94A3B8]">From Python Foundations to Intelligent Automation.</span>
          </span>
        </Link>

        <ul aria-label="The five learning pillars" className="relative my-auto w-full max-w-[340px] space-y-3 py-12 lg:py-0">
          {PILLARS.map((pillar) => {
            const active = activePillar === pillar;
            return (
              <li key={pillar} className="relative">
                <button
                  type="button"
                  aria-pressed={active}
                  aria-describedby={active && pillar === "Direct" ? "direct-tooltip" : undefined}
                  onMouseEnter={() => setActivePillar(pillar)}
                  onFocus={() => setActivePillar(pillar)}
                  onClick={() => setActivePillar(pillar)}
                  className={`relative flex h-[56px] w-full items-center gap-4 rounded-2xl px-3 text-left transition-colors ${
                    active ? "bg-[#1E2638] text-white" : "text-[#94A3B8] hover:bg-[#1E2638]/70"
                  }`}
                >
                  <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border bg-[#1E2436] ${active ? "border-[#2D3548] text-[#E06346]" : "border-[#2D3548]"}`}>
                    <span className="h-5 w-5"><PillarIcon name={pillar} /></span>
                  </span>
                  <span className="text-[17px] font-medium">{pillar}</span>
                  {active && pillar === "Direct" && <CursorIcon />}
                </button>
                {active && pillar === "Direct" && (
                  <div
                    id="direct-tooltip"
                    role="tooltip"
                    className="relative mt-2 max-w-[240px] rounded-xl border border-[#334155] bg-[#1B2130] px-4 py-3 text-[13px] leading-[1.55] text-white shadow-[0_12px_30px_rgba(0,0,0,0.28)] lg:absolute lg:left-[calc(100%+1rem)] lg:top-0 lg:mt-0 lg:w-[240px]"
                  >
                    <span className="absolute -top-1.5 left-5 h-3 w-3 rotate-45 border-l border-t border-[#334155] bg-[#1B2130] lg:left-[-7px] lg:top-5 lg:border-l lg:border-b-0 lg:border-t" />
                    Structure prompts, set guardrails, and guide AI agents with clear intent.
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      </section>

      <section className="flex min-h-[520px] items-center justify-center bg-[#FAFAFA] px-6 py-14 sm:px-12 lg:min-h-screen lg:px-14 xl:px-20">
        <div className="w-full max-w-[360px]">
          <h1 className="text-2xl font-semibold tracking-[-0.02em] text-[#0F172A]">{title}</h1>
          <p className="mt-1 text-sm text-[#64748B]">{subtitle}</p>
          <div className="mt-8">{children}</div>
          <p className="mt-6 text-center text-[13px] text-[#64748B]">{footer}</p>
        </div>
      </section>
    </main>
  );
}
