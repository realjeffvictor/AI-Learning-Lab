import type { MouseEvent } from "react";
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

const ENGINEER_TOMORROW = [
  {
    title: "THINK BEYOND CODE",
    summary: "Understand the principles behind software, not just the syntax used to create it.",
  },
  {
    title: "WORK WITH AI",
    summary: "Use AI to accelerate development, explore solutions and improve productivity without surrendering technical understanding.",
  },
  {
    title: "BUILD REAL SYSTEMS",
    summary: "Turn ideas into functional applications, connect technologies and solve problems that matter.",
  },
  {
    title: "VERIFY AND TAKE OWNERSHIP",
    summary: "Test, debug, evaluate and understand every system you build, whether AI helped create it or not.",
  },
  {
    title: "KEEP EVOLVING",
    summary: "Adapt to new technologies, learn continuously and stay capable in an industry that never stands still.",
  },
] as const;

function handleFooterAnchorClick(event: MouseEvent<HTMLAnchorElement>) {
  const target = document.getElementById(event.currentTarget.hash.slice(1));
  if (!target) return;

  event.preventDefault();
  window.history.replaceState(window.history.state, "", event.currentTarget.hash);
  target.scrollIntoView({
    behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
  });
}

export function HomePage() {
  const { status } = useAuth();
 // const authenticated = status === "authenticated";

  return (
    <main className="bg-[#FAFAFA]">
      <section className="relative isolate flex min-h-[720px] flex-col overflow-hidden bg-[#121622] px-6 py-7 text-white sm:px-12 sm:py-10 lg:min-h-screen lg:px-16 lg:py-12 xl:px-24">
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
          className="pointer-events-none absolute inset-0 z-[1] bg-gradient-to-l from-[#101725]/90 via-[#101725]/60 to-[#121622]/15"
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 z-[1] bg-gradient-to-b from-[#121622]/35 via-transparent to-[#121622]/85"
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
              to="/login"
              className="rounded-lg border border-[#394154] px-4 py-2 text-sm font-medium text-white transition-colors hover:border-[#94A3B8] hover:bg-[#1E2436]"
            >
              Sign in
            </Link>
          )}
        </header>

        <div className="home-hero-copy relative z-10 my-auto ml-auto w-full max-w-[560px] py-16">
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
                to="/register"
                className="inline-flex h-11 items-center justify-center rounded-lg bg-[#D95D39] px-5 text-sm font-semibold text-white transition-colors hover:bg-[#c84f2f]"
              >
                Create an account
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
        aria-labelledby="future-engineering-heading"
        className="bg-[#FAFAFA] px-6 py-14 sm:px-12 sm:py-16 lg:px-16 lg:py-20"
      >
        <div className="mx-auto max-w-6xl">
          <div className="max-w-3xl">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#D95D39]">
              THE FUTURE IS BEING BUILT NOW
            </p>
            <h2 id="future-engineering-heading" className="mt-3 text-2xl font-semibold leading-tight tracking-[-0.03em] text-[#0F172A] sm:text-3xl">
              Software engineering is evolving. Are you ready?
            </h2>
            <p className="mt-3 text-[13px] leading-[1.65] text-[#475569] sm:text-sm">
              AI is changing how software is designed, developed and delivered. The next generation of engineers won&apos;t
              just write code. They&apos;ll understand systems, direct intelligent tools, solve complex problems and take
              responsibility for what they build.
            </p>
          </div>

          <h3 className="mt-8 text-[13px] font-semibold text-[#0F172A]">
            The engineer of tomorrow will know how to:
          </h3>
          <ol aria-label="Skills of the engineer of tomorrow" className="mt-4 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
            {ENGINEER_TOMORROW.map((item) => (
              <li key={item.title} className="border-l-2 border-[#E2E8F0] pl-4">
                <h4 className="text-[11px] font-semibold tracking-[0.06em] text-[#0F172A]">{item.title}</h4>
                <p className="mt-1 text-xs leading-[1.6] text-[#64748B]">{item.summary}</p>
              </li>
            ))}
          </ol>

          <div className="mt-8 border-t border-[#E2E8F0] pt-5">
            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#D95D39]">
              THE AI LEARNING LAB APPROACH
            </p>
            <p className="mt-2 text-[13px] font-semibold leading-5 text-[#0F172A]">
              Learn the fundamentals. Master the tools. Build with intelligence. Own the outcome.
            </p>
            <p className="mt-2 border-l-2 border-[#D95D39] pl-3 text-xs italic leading-5 text-[#64748B]">
              Don&apos;t just learn to code for today&apos;s technology. Develop the ability to build for what comes next.
            </p>
          </div>
        </div>
      </section>

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
                to="/register"
                className="inline-flex h-11 items-center justify-center rounded-lg bg-[#D95D39] px-5 text-sm font-semibold text-white transition-colors hover:bg-[#c84f2f]"
              >
                Start learning
              </Link>
            </div>
          )}
        </div>
      </section>

      <footer className="bg-[#121622] px-6 py-14 text-white sm:px-12 lg:px-16">
        <div className="mx-auto max-w-6xl">
          <div className="grid gap-10 md:grid-cols-[1.4fr_1fr]">
            <section aria-label="AI Learning Lab contact information">
              <Link to="/" className="flex w-fit items-center gap-3 text-white no-underline">
                <svg viewBox="0 0 48 40" className="h-9 w-11 shrink-0 text-[#E06346]" fill="currentColor" aria-hidden="true">
                  <path d="M24 2 1 13l23 11 18-8.6V29h4V13L24 2Zm-15 17v9c0 5 7 9 15 9s15-4 15-9v-9l-15 7-15-7Z" />
                  <circle cx="44" cy="31" r="3" />
                </svg>
                <span className="text-lg font-semibold tracking-[-0.02em]">AI Learning Lab</span>
              </Link>
              <p className="mt-4 max-w-md text-sm leading-6 text-[#B5BECE]">
                From Python Foundations to Intelligent Automation. Practical AI engineering training for builders.
              </p>
              <div className="mt-5 flex flex-wrap gap-x-6 gap-y-2 text-[13px] text-[#94A3B8]">
                <a
                  href="https://wa.me/2348063789600"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition-colors hover:text-white"
                >
                  +234 806 378 9600
                </a>
                <a
                  href="https://linkedin.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition-colors hover:text-white"
                >
                  LinkedIn
                </a>
              </div>
            </section>

            <nav aria-label="Footer" className="md:justify-self-end md:w-full md:max-w-[220px]">
              <h2 className="text-[15px] font-semibold text-white">Quick Links</h2>
              <ul className="mt-4 space-y-2.5 text-sm text-[#B5BECE]">
                <li><Link to="/about" className="transition-colors hover:text-[#E06346]">About Us</Link></li>
                <li><Link to="/contact" className="transition-colors hover:text-[#E06346]">Contact Us</Link></li>
                <li><a href="#curriculum-highlights" onClick={handleFooterAnchorClick} className="transition-colors hover:text-[#E06346]">Curriculum</a></li>
                <li><a href="#learning-pillars" onClick={handleFooterAnchorClick} className="transition-colors hover:text-[#E06346]">The 5 Pillars</a></li>
                <li><Link to="/register" className="transition-colors hover:text-[#E06346]">Create an Account</Link></li>
                <li><Link to="/login" className="transition-colors hover:text-[#E06346]">Student Sign In</Link></li>
              </ul>
            </nav>
          </div>

          <div className="mt-10 flex flex-col items-center justify-between gap-4 border-t border-[#2D3548] pt-6 text-xs text-[#7F8BA1] sm:flex-row">
            <p>© 2026 Light City. All rights reserved.</p>
            <p>
              Powered by{" "}
              <Link to="/about" className="font-semibold text-white transition-colors hover:underline">
                Light City
              </Link>
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}
