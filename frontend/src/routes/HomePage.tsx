import { Link } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";
import { PRINCIPLES } from "../lib/principles";
import "./HomePage.css";

const CURRICULUM_STAGES = [
  {
    title: "Python Fundamentals",
    summary: "Learn to think in steps and express them in Python: values, control flow, functions, objects and files.",
  },
  {
    title: "Data Manipulation",
    summary: "Load, clean, transform and analyse structured data with CSV, JSON, NumPy and Pandas.",
  },
  {
    title: "APIs and External Systems",
    summary: "Understand how software talks to other software: HTTP, REST, authentication, webhooks and databases.",
  },
  {
    title: "AI Models",
    summary: "From machine learning basics to language models, prompting, embeddings, retrieval and agents.",
  },
  {
    title: "AI-Powered Automation",
    summary: "Design, build, deploy and monitor automated workflows, including multi-step AI workflows with human approval.",
  },
] as const;

export function HomePage() {
  const { status } = useAuth();
  const authenticated = status === "authenticated";

  return (
    <main className="bg-[#FAFAFA]">
      <div className="grid min-h-screen lg:grid-cols-[55fr_45fr]">
        <section className="relative isolate flex min-h-[640px] flex-col overflow-hidden bg-[#121622] px-7 py-8 text-white sm:px-12 sm:py-10 lg:min-h-screen lg:px-[clamp(3rem,6vw,6rem)] lg:py-12">
          <img
            src="/images/ai-learning-lab-hero.jpeg"
            alt=""
            aria-hidden="true"
            fetchPriority="high"
            decoding="async"
            className="home-hero-image pointer-events-none absolute inset-0 z-0 h-full w-full object-cover object-[52%_center]"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 z-[1] bg-gradient-to-r from-[#101725]/80 via-[#101725]/58 to-[#121622]/38"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 z-[1] bg-gradient-to-b from-[#121622]/35 via-transparent to-[#121622]/80"
          />
          <header className="home-hero-header relative z-10 flex items-center justify-between gap-5">
            <Link to="/" className="flex w-fit items-center gap-3 rounded-sm text-white no-underline">
              <svg viewBox="0 0 48 40" className="h-9 w-11 shrink-0 text-[#E06346]" fill="currentColor" aria-hidden="true">
                <path d="M24 2 1 13l23 11 18-8.6V29h4V13L24 2Zm-15 17v9c0 5 7 9 15 9s15-4 15-9v-9l-15 7-15-7Z" />
                <circle cx="44" cy="31" r="3" />
              </svg>
              <span className="text-lg font-semibold tracking-[-0.02em]">AI Learning Lab</span>
            </Link>
            {status !== "loading" && (
              <Link
                to={authenticated ? "/dashboard" : "/login"}
                className="rounded-lg border border-[#394154] px-4 py-2 text-sm font-medium text-white transition-colors hover:border-[#94A3B8] hover:bg-[#1E2436]"
              >
                {authenticated ? "Dashboard" : "Sign in"}
              </Link>
            )}
          </header>

          <div className="home-hero-copy relative z-10 my-auto max-w-[560px] py-16">
            <p className="mb-5 text-xs font-semibold uppercase tracking-[0.18em] text-[#E88A70]">A practical path into AI</p>
            <h1 className="text-4xl font-semibold leading-[1.12] tracking-[-0.04em] sm:text-5xl">
              Build the skills to put AI to work.
            </h1>
            <p className="mt-6 max-w-lg text-base leading-7 text-[#B5BECE] sm:text-lg">
              From Python Foundations to Intelligent Automation.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-3">
              {status !== "loading" && (
                <Link
                  to={authenticated ? "/dashboard" : "/register"}
                  className="inline-flex h-11 items-center justify-center rounded-lg bg-[#D95D39] px-5 text-sm font-semibold text-white transition-colors hover:bg-[#c84f2f]"
                >
                  {authenticated ? "Open dashboard" : "Create an account"}
                </Link>
              )}
              <a
                href="#curriculum-highlights"
                className="inline-flex h-11 items-center justify-center rounded-lg border border-[#394154] px-5 text-sm font-medium text-[#E2E8F0] transition-colors hover:bg-[#1E2436]"
              >
                Explore the learning path
              </a>
            </div>
          </div>

          <div id="learning-pillars" className="relative z-10 border-t border-[#2D3548] pt-5">
            <p className="mb-3 text-xs font-medium uppercase tracking-[0.14em] text-[#7F8BA1]">The learning pillars</p>
            <ol className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-5">
              {PRINCIPLES.map(([, name], index) => (
                <li key={name} className="flex items-center gap-2 text-sm text-[#C2CAD7]">
                  <span className="font-mono text-[10px] text-[#E06346]">{String(index + 1).padStart(2, "0")}</span>
                  <span>{name}</span>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section
          aria-labelledby="learning-path-preview"
          className="flex min-h-[600px] items-center justify-center px-6 py-14 sm:px-12 lg:min-h-screen lg:px-14 lg:py-4 xl:px-20"
        >
          <div className="w-full max-w-[460px]">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#D95D39]">The learning path</p>
            <h2 id="learning-path-preview" className="mt-3 text-2xl font-semibold tracking-[-0.02em] text-[#0F172A]">
              Build capability, one stage at a time.
            </h2>
            <p className="mt-2 text-sm leading-6 text-[#64748B]">
              Start with Python, then progress through data, APIs, AI models and automation.
            </p>

            <div className="mt-6 overflow-hidden rounded-2xl border border-[#E2E8F0] bg-white shadow-[0_12px_36px_rgba(15,23,42,0.06)]">
              <ol aria-label="Five curriculum stages" className="relative space-y-1 px-5 py-5 sm:px-6">
                <span aria-hidden="true" className="absolute bottom-10 left-[39px] top-10 w-px bg-[#E2E8F0] sm:left-[43px]" />
                {CURRICULUM_STAGES.map((stage, index) => (
                  <li key={stage.title} className="relative flex gap-4 py-2">
                    <span className="z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-[#F2C8BC] bg-[#FFF6F2] font-mono text-[10px] font-semibold text-[#D95D39]">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <div className="min-w-0 pt-0.5">
                      <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[#94A3B8]">
                        Stage {index + 1}
                      </p>
                      <h3 className="mt-0.5 text-sm font-semibold text-[#0F172A]">{stage.title}</h3>
                      <p className="mt-1 line-clamp-1 text-xs leading-5 text-[#64748B]">{stage.summary}</p>
                    </div>
                  </li>
                ))}
              </ol>

              <div className="border-t border-[#E2E8F0] bg-[#F8FAFC] px-5 py-4 sm:px-6">
                <p className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[#D95D39]">
                  Runs alongside every stage
                </p>
                <h3 className="mt-1 text-sm font-semibold text-[#0F172A]">AI-Assisted Software Engineering</h3>
                <p className="mt-1 text-xs leading-5 text-[#64748B]">
                  Learn to direct AI well and take ownership of the software you build.
                </p>
              </div>
            </div>

            <a
              href="#curriculum-highlights"
              className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[#D95D39] underline underline-offset-4 hover:text-[#B9482B]"
            >
              Explore all curriculum highlights
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M5 12h14m-6-6 6 6-6 6" />
              </svg>
            </a>
          </div>
        </section>
      </div>

      <section
        id="curriculum-highlights"
        aria-labelledby="curriculum-heading"
        className="scroll-mt-8 bg-[#F1F4F8] px-6 py-16 sm:px-12 sm:py-20 lg:px-16"
      >
        <div className="mx-auto max-w-6xl">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#D95D39]">Curriculum at a glance</p>
          <h2 id="curriculum-heading" className="mt-3 max-w-2xl text-3xl font-semibold tracking-[-0.03em] text-[#0F172A] sm:text-4xl">
            A clear route from Python to applied AI.
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-7 text-[#64748B]">
            Build your foundations, work with data and APIs, then put AI models and automation into practice.
          </p>

          <ol className="mt-9 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {CURRICULUM_STAGES.map((stage, index) => (
              <li key={stage.title} className="rounded-2xl border border-[#E2E8F0] bg-white p-5 sm:p-6">
                <p className="font-mono text-xs font-medium text-[#D95D39]">
                  STAGE {String(index + 1).padStart(2, "0")}
                </p>
                <h3 className="mt-3 text-lg font-semibold text-[#0F172A]">{stage.title}</h3>
                <p className="mt-2 text-sm leading-6 text-[#64748B]">{stage.summary}</p>
              </li>
            ))}
          </ol>

          <aside className="mt-5 flex flex-col gap-3 rounded-2xl border border-[#2D3548] bg-[#121622] p-5 text-white sm:flex-row sm:items-center sm:gap-6 sm:p-6">
            <span className="shrink-0 font-mono text-xs font-medium uppercase tracking-wide text-[#E88A70]">
              Runs alongside every stage
            </span>
            <div>
              <h3 className="font-semibold">AI-Assisted Software Engineering</h3>
              <p className="mt-1 text-sm leading-6 text-[#B5BECE]">
                Direct AI well and keep ownership of what you build, from design and testing to review and maintenance.
              </p>
            </div>
          </aside>

          {status !== "loading" && (
            <div className="mt-8">
              <Link
                to={authenticated ? "/dashboard" : "/register"}
                className="inline-flex h-11 items-center justify-center rounded-lg bg-[#D95D39] px-5 text-sm font-semibold text-white transition-colors hover:bg-[#c84f2f]"
              >
                {authenticated ? "Open dashboard" : "Start learning"}
              </Link>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
