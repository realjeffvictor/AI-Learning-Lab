import { Link } from "react-router-dom";

const CORE_PILLARS = [
  {
    title: "Client Satisfaction as a Driving Force",
    description:
      "Every product, service, and learning experience is built around client trust, real outcomes, and lasting satisfaction.",
  },
  {
    title: "Abuja Roots, Global Vision",
    description:
      "Headquartered in Abuja with an outlook built to serve, collaborate, and compete globally.",
  },
  {
    title: "A People-First Tech Community",
    description:
      "Bringing together passionate builders, engineers, and problem-solvers to grow and create impactful solutions.",
  },
] as const;

export function AboutPage() {
  return (
    <main className="min-h-screen bg-[#FAFAFA] text-[#0F172A]">
      <header className="border-b border-[#E2E8F0]">
        <nav aria-label="Main" className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-5 sm:px-12 lg:px-16">
          <Link to="/" className="font-semibold text-[#121622]">AI Learning Lab</Link>
          <div className="flex items-center gap-5 text-sm">
            <Link to="/" className="text-[#475569] transition-colors hover:text-[#D95D39]">Home</Link>
            <Link to="/login" className="rounded-lg bg-[#D95D39] px-4 py-2 font-semibold text-white transition-colors hover:bg-[#c84f2f]">
              Sign in
            </Link>
          </div>
        </nav>
      </header>

      <section className="bg-[#121622] px-6 py-16 text-white sm:px-12 sm:py-20 lg:px-16 lg:py-24">
        <div className="mx-auto max-w-6xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#E06346]">ABOUT LIGHT CITY</p>
          <h1 className="mt-4 max-w-4xl text-4xl font-semibold leading-tight tracking-[-0.035em] sm:text-5xl">
            Rooted in Abuja. Building technology with a global vision.
          </h1>
          <p className="mt-6 max-w-3xl text-base leading-7 text-[#B5BECE]">
            Light City is a technology company based in Abuja, Nigeria, with a global vision. We are building a dedicated
            community of people united by excellence, innovation, and client satisfaction as one of our major driving
            forces.
          </p>
        </div>
      </section>

      <section aria-label="Light City core pillars" className="px-6 py-14 sm:px-12 sm:py-16 lg:px-16 lg:py-20">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-2xl font-semibold tracking-tight text-[#0F172A]">What guides us</h2>
          <ul className="mt-7 grid gap-5 md:grid-cols-3">
            {CORE_PILLARS.map((pillar) => (
              <li key={pillar.title} className="rounded-2xl border border-[#E2E8F0] bg-white p-6">
                <h3 className="text-lg font-semibold leading-snug text-[#0F172A]">{pillar.title}</h3>
                <p className="mt-3 text-sm leading-6 text-[#475569]">{pillar.description}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <footer className="mx-auto mt-8 flex max-w-6xl flex-col items-center justify-between gap-4 border-t border-[#E2E8F0] px-6 py-6 text-xs text-[#64748B] sm:flex-row sm:px-12 lg:px-16">
        <p>© 2026 Light City. All rights reserved.</p>
        <p>
          Powered by{" "}
          <Link to="/about" className="font-semibold text-[#0F172A] hover:underline">Light City</Link>
        </p>
      </footer>
    </main>
  );
}
