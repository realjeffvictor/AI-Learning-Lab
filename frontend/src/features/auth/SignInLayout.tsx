import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";

type Pillar = "Understand" | "Direct" | "Build" | "Verify" | "Own";

const PILLARS: Pillar[] = ["Understand", "Direct", "Build", "Verify", "Own"];

const PILLAR_SUMMARIES: Record<Pillar, string> = {
  Understand:
    "Master core Python, system architecture, and how LLMs reason—so you never rely on blind copy-pasting.",
  Direct:
    "Decompose complex problems, engineer rich context, and steer AI coding agents with clear specifications.",
  Build:
    "Ship real-world Python applications, APIs, RAG pipelines, and autonomous workflows from scratch.",
  Verify:
    "Audit, test, and debug AI-generated code with precision to catch hallucinations, security flaws, and edge cases.",
  Own:
    "Deploy, monitor, and maintain production-grade software with full architectural accountability.",
};

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
  const [activePillar, setActivePillar] = useState<Pillar | null>(null);

  return (
    <main className="grid min-h-screen bg-[#FAFAFA] lg:grid-cols-[55fr_45fr]">
      <section className="relative flex min-h-[560px] flex-col overflow-hidden bg-[#121622] px-7 py-10 text-white sm:px-12 sm:py-12 lg:min-h-screen lg:px-[clamp(3rem,6vw,6rem)] lg:py-14">
        <svg
          viewBox="0 0 900 280"
          preserveAspectRatio="none"
          className="pointer-events-none absolute inset-x-0 bottom-0 z-0 h-[220px] w-full sm:h-[250px] lg:h-[230px]"
          aria-hidden="true"
        >
          <defs>
            <linearGradient id="sidebar-wave-navy" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#1B2940" />
              <stop offset="0.55" stopColor="#182238" />
              <stop offset="1" stopColor="#111827" />
            </linearGradient>
            <linearGradient id="sidebar-wave-orange" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stopColor="#E66B3F" />
              <stop offset="0.48" stopColor="#D95D39" />
              <stop offset="1" stopColor="#A84435" />
            </linearGradient>
            <linearGradient id="sidebar-wave-highlight" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stopColor="#FF956B" stopOpacity="0.65" />
              <stop offset="0.6" stopColor="#F17A56" stopOpacity="0.32" />
              <stop offset="1" stopColor="#E06346" stopOpacity="0.08" />
            </linearGradient>
          </defs>
          <path
            d="M-20 204 C130 174 222 244 372 243 C530 242 640 174 772 145 C828 133 875 134 920 142 L920 300 L-20 300 Z"
            fill="url(#sidebar-wave-navy)"
          />
          <path
            d="M-20 168 C84 132 164 166 266 198 C380 234 474 235 588 190 C704 144 805 104 920 112 L920 159 C802 153 708 197 594 228 C478 263 374 267 258 230 C150 195 80 164 -20 248 L-20 300 L0 300 L0 238 Z"
            fill="url(#sidebar-wave-orange)"
          />
          <path
            d="M-10 174 C88 140 164 174 270 205 C383 238 478 239 591 195 C703 152 806 112 910 118"
            fill="none"
            stroke="url(#sidebar-wave-highlight)"
            strokeWidth="3"
          />
        </svg>
        <Link to="/" className="relative z-10 flex w-fit items-center gap-4 rounded-sm text-white no-underline">
          <svg viewBox="0 0 48 40" className="h-10 w-12 shrink-0 text-[#E06346]" fill="currentColor" aria-hidden="true">
            <path d="M24 2 1 13l23 11 18-8.6V29h4V13L24 2Zm-15 17v9c0 5 7 9 15 9s15-4 15-9v-9l-15 7-15-7Z" />
            <circle cx="44" cy="31" r="3" />
          </svg>
          <span>
            <span className="block text-[26px] font-semibold leading-tight tracking-[-0.03em]">AI Learning Lab</span>
            <span className="mt-1 block text-sm text-[#94A3B8]">From Python Foundations to Intelligent Automation.</span>
          </span>
        </Link>

        <ul aria-label="The five learning pillars" className="relative z-10 my-auto w-full max-w-[340px] space-y-3 py-12 lg:py-0">
          {PILLARS.map((pillar) => {
            const active = activePillar === pillar;
            const summaryId = `pillar-summary-${pillar.toLowerCase()}`;
            return (
              <li key={pillar} className="relative">
                <button
                  type="button"
                  aria-pressed={active}
                  aria-describedby={active ? summaryId : undefined}
                  onMouseEnter={() => setActivePillar(pillar)}
                  onFocus={() => setActivePillar(pillar)}
                  onClick={() => setActivePillar(pillar)}
                  onMouseLeave={() => setActivePillar((current) => current === pillar ? null : current)}
                  onBlur={() => setActivePillar((current) => current === pillar ? null : current)}
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
                <div
                  id={summaryId}
                  role="tooltip"
                  aria-hidden={!active}
                  className={`absolute left-[calc(100%+14px)] top-1/2 z-20 w-[260px] -translate-y-1/2 rounded-[12px] border border-[#334155] bg-[#1B2130] p-[12px_16px] text-[13px] leading-[1.55] text-white shadow-[0_10px_25px_rgba(0,0,0,0.35)] transition-[opacity,transform,visibility] duration-150 pointer-events-none ${
                    active
                      ? "visible translate-x-0 opacity-100 max-md:static max-md:mt-2 max-md:w-full max-md:translate-y-0"
                      : "invisible translate-x-1 opacity-0 max-md:absolute max-md:left-0 max-md:top-full max-md:mt-2"
                  }`}
                >
                  <span className="absolute -left-[7px] top-1/2 h-3 w-3 -translate-y-1/2 rotate-45 border-b border-l border-[#334155] bg-[#1B2130] max-md:hidden" />
                  {PILLAR_SUMMARIES[pillar]}
                </div>
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
