import { Link } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";
import { StatusPanel } from "../features/health/StatusPanel";
import { PRINCIPLES } from "../lib/principles";

export function HomePage() {
  const { status } = useAuth();
  const authenticated = status === "authenticated";

  return (
    <main className="grid min-h-screen bg-[#FAFAFA] lg:grid-cols-[55fr_45fr]">
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
              href="#learning-pillars"
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
    </main>
  );
}
