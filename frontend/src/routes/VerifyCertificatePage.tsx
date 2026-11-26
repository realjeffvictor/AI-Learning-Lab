import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Button } from "../components/Button";
import { Loading } from "../components/StateMessage";
import { verifyCertificate } from "../features/certificates/api";
import { ApiError } from "../lib/api/errors";

/** Public page: no sign-in. Shows only the holder's name, the course and the date. */
export function VerifyCertificatePage() {
  const { code } = useParams();
  const certificate = useQuery({
    queryKey: ["verify", code],
    queryFn: ({ signal }) => verifyCertificate(code as string, signal),
    enabled: Boolean(code),
  });

  return (
    <main className="mx-auto max-w-2xl px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">AI Learning Lab. Certificate check</p>
      {certificate.isPending && <div className="mt-6"><Loading label="Checking" /></div>}
      {certificate.isError && (
        <div className="mt-6">
          <h1 className="font-serif text-3xl">Not verified</h1>
          <p className="mt-2 text-ink-muted">
            {certificate.error instanceof ApiError && certificate.error.status === 429
              ? "Too many checks from this connection. Wait a minute and try again."
              : "No certificate matches this code. Check the link and try again."}
          </p>
        </div>
      )}
      {certificate.data && (
        <article className="mt-6 border-y border-rule py-8">
          <p className="font-mono text-xs uppercase tracking-widest text-ok">Verified</p>
          <h1 className="mt-3 font-serif text-4xl leading-tight">{certificate.data.holder_name}</h1>
          <p className="mt-3 text-ink-muted">completed the course</p>
          <p className="mt-1 font-serif text-2xl">{certificate.data.course_title}</p>
          <p className="mt-4 font-mono text-xs text-ink-muted">
            Issued {new Date(certificate.data.issued_at).toLocaleDateString()}. Verification code {code}.
          </p>
          <p className="mt-4 max-w-md text-sm text-ink-muted">
            Awarded after every written lesson, every quiz and puzzle, and a reviewed project were completed on the platform.
          </p>
          <div className="mt-6 flex gap-3">
            <Button onClick={() => window.print()}>Print</Button>
          </div>
        </article>
      )}
      <p className="mt-8 text-sm">
        <Link to="/" className="text-signal underline underline-offset-4">AI Learning Lab</Link>
      </p>
    </main>
  );
}
