import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button } from "../../components/Button";
import { ErrorNote, Loading } from "../../components/StateMessage";
import { fetchCertificates, issueCertificate } from "./api";
import { unmet, verifyPath } from "./utils";

export function CertificatesSection() {
  const queryClient = useQueryClient();
  const certificates = useQuery({ queryKey: ["certificates"], queryFn: ({ signal }) => fetchCertificates(signal) });
  const issue = useMutation({
    mutationFn: (courseSlug: string) => issueCertificate(courseSlug),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["certificates"] });
      void queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  return (
    <section className="mt-10" aria-labelledby="certificates-heading">
      <h2 id="certificates-heading" className="mb-1 font-mono text-xs uppercase tracking-widest text-ink-muted">
        Certificates
      </h2>
      <p className="max-w-2xl text-sm text-ink-muted">
        A certificate needs every written lesson completed, every quiz and puzzle passed, and every project approved by a
        reviewer. Code exercises are self-reported, so they do not count toward it. Anyone with the link can verify it.
      </p>
      {certificates.isPending && <Loading label="Loading certificates" />}
      {certificates.isError && <ErrorNote error={certificates.error} />}
      {certificates.data && (
        <ul className="mt-3 divide-y divide-rule border-y border-rule text-sm">
          {certificates.data.map((item) => (
            <li key={item.course_slug} className="py-3">
              <div className="flex flex-wrap items-baseline justify-between gap-3">
                <span className="font-serif text-lg">{item.course_title}</span>
                {item.certificate && <span className="font-mono text-xs uppercase tracking-widest text-ok">Issued</span>}
              </div>
              {item.certificate ? (
                <p className="mt-1">
                  <Link to={verifyPath(item.certificate.code)} className="text-signal underline underline-offset-4">
                    View and share your certificate
                  </Link>
                  <span className="ml-2 break-all font-mono text-xs text-ink-muted">
                    {window.location.origin}
                    {verifyPath(item.certificate.code)}
                  </span>
                </p>
              ) : (
                <>
                  <ul className="mt-1 font-mono text-xs text-ink-muted">
                    {item.requirements.map((requirement) => (
                      <li key={requirement.key}>
                        {requirement.label}: {requirement.done}/{requirement.total}
                      </li>
                    ))}
                  </ul>
                  {item.eligible ? (
                    <div className="mt-2">
                      <Button onClick={() => issue.mutate(item.course_slug)} disabled={issue.isPending}>
                        {issue.isPending ? "Issuing..." : "Issue certificate"}
                      </Button>
                    </div>
                  ) : (
                    <p className="mt-1 text-xs text-ink-muted">
                      {item.message ?? `${unmet(item.requirements).length} requirement(s) left.`}
                    </p>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
      )}
      {issue.isError && <ErrorNote error={issue.error} />}
    </section>
  );
}
