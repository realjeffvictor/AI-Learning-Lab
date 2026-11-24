import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="mx-auto max-w-[1200px] px-6 py-24">
      <p className="font-mono text-sm text-ink-muted">404</p>
      <h1 className="mt-2 font-serif text-3xl">Page not found</h1>
      <Link to="/" className="mt-6 inline-block text-signal underline underline-offset-4">
        Back to start
      </Link>
    </main>
  );
}
