import { Link } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";
import { StatusPanel } from "../features/health/StatusPanel";
import { PRINCIPLES } from "../lib/principles";

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
        <section className="flex min-h-[640px] flex-col bg-[#121622] px-7 py-8 text-white sm:px-12 sm:py-10 lg:min-h-screen lg:px-[clamp(3rem,6vw,6rem)] lg:py-12">
          <header className="flex items-center justify-between gap-5">
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

          <div className="my-auto max-w-[560px] py-16">
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

          <div id="learning-pillars" className="border-t border-[#2D3548] pt-5">
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

        <section className="flex min-h-[600px] items-center justify-center px-6 py-14 sm:px-12 lg:min-h-screen lg:px-14 xl:px-20">
          <div className="w-full max-w-[420px]">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#D95D39]">Your workspace</p>
            <h2 className="mt-3 text-2xl font-semibold tracking-[-0.02em] text-[#0F172A]">Ready when you are.</h2>
            <p className="mt-2 text-sm leading-6 text-[#64748B]">
              Check the learning environment and explore a clear path from foundations to applied AI.
            </p>

            <div className="mt-7 rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-[0_12px_36px_rgba(15,23,42,0.06)] sm:p-6">
              <StatusPanel />
            </div>

            <p className="mt-6 text-center text-sm text-[#64748B]">
              {authenticated ? (
                <Link to="/dashboard" className="font-medium text-[#D95D39] underline underline-offset-4">
                  Continue to your dashboard
                </Link>
              ) : (
                <>
                  New to AI Learning Lab?{" "}
                  <Link to="/register" className="font-medium text-[#D95D39] underline underline-offset-4">
                    Create an account
                  </Link>
                </>
              )}
            </p>
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
