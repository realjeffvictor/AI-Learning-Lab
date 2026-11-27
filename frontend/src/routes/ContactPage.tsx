import { Link } from "react-router-dom";

const SOCIAL_LINKS = [
  {
    name: "WhatsApp",
    value: "+234 806 378 9600",
    href: "https://wa.me/2348063789600",
    label: "Chat with us directly on WhatsApp",
  },
  {
    name: "LinkedIn",
    value: "linkedin.com",
    href: "https://linkedin.com",
    label: "Connect with us on LinkedIn",
  },
  // { name: "X / Twitter", value: "@your-handle", href: "https://x.com/your-handle", label: "Follow us on X" },
  // { name: "Instagram", value: "@your-handle", href: "https://instagram.com/your-handle", label: "Follow us on Instagram" },
  // { name: "Email", value: "hello@example.com", href: "mailto:hello@example.com", label: "Email our team" },
] as const;

export function ContactPage() {
  return (
    <main className="flex min-h-screen flex-col bg-[#FAFAFA] text-[#0F172A]">
      <header className="border-b border-[#E2E8F0]">
        <nav aria-label="Main" className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-5 sm:px-12 lg:px-16">
          <Link to="/" className="font-semibold text-[#121622]">AI Learning Lab</Link>
          <div className="flex items-center gap-5 text-sm">
            <Link to="/" className="text-[#475569] transition-colors hover:text-[#D95D39]">Home</Link>
            <Link to="/about" className="text-[#475569] transition-colors hover:text-[#D95D39]">About Us</Link>
          </div>
        </nav>
      </header>

      <section className="flex-1 px-6 py-14 sm:px-12 sm:py-16 lg:px-16 lg:py-20">
        <div className="mx-auto max-w-6xl">
          <div className="rounded-2xl bg-[#121622] px-6 py-10 text-white sm:px-10 sm:py-12">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#E06346]">CONTACT LIGHT CITY</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-[-0.035em] sm:text-5xl">Get in Touch</h1>
            <p className="mt-4 max-w-2xl text-sm leading-6 text-[#B5BECE] sm:text-base">
              Reach out to Light City &amp; AI Learning Lab through any of our official channels below.
            </p>
          </div>

          <ul className="mt-8 grid gap-4 md:grid-cols-2">
            {SOCIAL_LINKS.map((link) => (
              <li key={link.name}>
                <a
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex h-full flex-col rounded-2xl border border-[#E2E8F0] bg-white p-6 transition-colors hover:border-[#D95D39]"
                >
                  <span className="text-xs font-semibold uppercase tracking-[0.14em] text-[#D95D39]">{link.name}</span>
                  <span className="mt-2 text-xl font-semibold text-[#0F172A] group-hover:text-[#D95D39]">{link.value}</span>
                  <span className="mt-2 text-sm text-[#64748B]">{link.label}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <footer className="mx-auto flex w-full max-w-6xl flex-col items-center justify-between gap-4 border-t border-[#E2E8F0] px-6 py-6 text-xs text-[#64748B] sm:flex-row sm:px-12 lg:px-16">
        <p>© 2026 Light City. All rights reserved.</p>
        <p>
          Powered by{" "}
          <Link to="/about" className="font-semibold text-[#0F172A] hover:underline">Light City</Link>
        </p>
      </footer>
    </main>
  );
}
