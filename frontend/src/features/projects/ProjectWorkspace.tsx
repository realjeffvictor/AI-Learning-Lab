import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Button } from "../../components/Button";
import { ErrorNote } from "../../components/StateMessage";
import { LessonMarkdown } from "../curriculum/LessonMarkdown";
import { saveDraft, submitProject } from "./api";
import { ProjectStatusTag } from "./ProjectStatusTag";
import { RUBRIC, SCORE_LABEL, type ProjectDetail, type ProjectStatus, type ReviewRead, type SubmissionDraft } from "./types";
import { DOCUMENTATION_LABEL, KIND_LABEL, checklistProgress, isEditable, submitProblems } from "./utils";

const AREA = "rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink disabled:opacity-60";

function ReviewHistory({ reviews }: { reviews: ReviewRead[] }) {
  if (reviews.length === 0) return null;
  return (
    <section aria-label="Review feedback">
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Reviewer feedback</p>
      <ol className="mt-2 space-y-4">
        {reviews.map((review) => (
          <li key={review.id} className="border-l-2 border-rule pl-3 text-sm">
            <p className={review.outcome === "approved" ? "text-ok" : "text-warn"}>
              {review.outcome === "approved" ? "Approved" : "Changes requested"}
              <span className="text-ink-muted">
                {" "}
                by {review.reviewer_name ?? "a reviewer"}, {new Date(review.created_at).toLocaleDateString()}
              </span>
            </p>
            <ul className="mt-1 font-mono text-xs text-ink-muted">
              {RUBRIC.map((item) => (
                <li key={item.key}>
                  {item.label}: {review.rubric_scores[item.key]}/4 {SCORE_LABEL[review.rubric_scores[item.key]] ?? ""}
                </li>
              ))}
            </ul>
            <p className="mt-2 whitespace-pre-wrap">{review.feedback}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

export function ProjectWorkspace({ detail }: { detail: ProjectDetail }) {
  const queryClient = useQueryClient();
  const saved = detail.submission;
  const status: ProjectStatus = saved?.status ?? "not_started";
  const editable = isEditable(status);

  const [repoUrl, setRepoUrl] = useState(saved?.repo_url ?? "");
  const [documentation, setDocumentation] = useState(saved?.documentation_md ?? "");
  const [reflection, setReflection] = useState(saved?.reflection_md ?? "");
  const [checks, setChecks] = useState<Record<string, boolean>>(saved?.requirement_checks ?? {});

  const draft = (): SubmissionDraft => ({
    repo_url: detail.requires_repo ? repoUrl : undefined,
    documentation_md: documentation,
    reflection_md: reflection,
    requirement_checks: checks,
  });

  function refresh() {
    void queryClient.invalidateQueries({ queryKey: ["project", detail.course_slug, detail.slug] });
    void queryClient.invalidateQueries({ queryKey: ["projects"] });
    void queryClient.invalidateQueries({ queryKey: ["achievements"] });
  }

  const save = useMutation({ mutationFn: () => saveDraft(detail.id, draft()), onSuccess: refresh });
  const submit = useMutation({
    mutationFn: async () => {
      await saveDraft(detail.id, draft());
      return submitProject(detail.id);
    },
    onSuccess: refresh,
  });

  const progress = checklistProgress(detail.requirements, checks);
  const problems = submitProblems(
    { repoUrl, documentation, reflection, checks },
    {
      kind: detail.kind,
      requirements: detail.requirements,
      minDocumentation: detail.min_documentation_chars,
      minReflection: detail.min_reflection_chars,
    },
  );
  const busy = save.isPending || submit.isPending;

  return (
    <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_20rem]">
      <article>
        <nav aria-label="Breadcrumb" className="font-mono text-xs text-ink-muted">
          <Link to="/projects" className="hover:text-ink">
            Projects
          </Link>{" "}
          / {detail.title}
        </nav>
        <p className="mt-3 font-mono text-xs uppercase tracking-widest text-signal">{KIND_LABEL[detail.kind]}</p>
        <h1 className="mt-1 font-serif text-4xl leading-tight">{detail.title}</h1>
        <p className="mt-2 max-w-2xl font-serif text-lg text-ink-muted">{detail.summary}</p>

        <div className="mt-8">
          <LessonMarkdown source={detail.brief_md} />
        </div>

        <section aria-labelledby="work-heading" className="mt-12 border-t border-rule pt-6">
          <h2 id="work-heading" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
            Your work
          </h2>
          {!editable && (
            <p role="status" className="mt-2 text-sm text-ink-muted">
              {status === "submitted"
                ? "Submitted. It is locked while it waits for a reviewer."
                : "Approved. This submission is final."}
            </p>
          )}

          <div className="mt-4 flex flex-col gap-5">
            {detail.requires_repo && (
              <div className="flex flex-col gap-1">
                <label htmlFor="repo" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
                  GitHub repository link
                </label>
                <input
                  id="repo"
                  type="url"
                  value={repoUrl}
                  disabled={!editable}
                  onChange={(event) => setRepoUrl(event.target.value)}
                  placeholder="https://github.com/yourname/your-project"
                  className={AREA}
                />
                <p className="text-xs text-ink-muted">Public repositories only. A reviewer will open this link.</p>
              </div>
            )}

            <div className="flex flex-col gap-1">
              <label htmlFor="docs" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
                {DOCUMENTATION_LABEL[detail.kind]}
              </label>
              <textarea
                id="docs"
                rows={14}
                maxLength={20000}
                value={documentation}
                disabled={!editable}
                onChange={(event) => setDocumentation(event.target.value)}
                className={`${AREA} font-mono text-sm`}
              />
              <p className="text-xs text-ink-muted">
                Markdown is fine. {documentation.trim().length} / {detail.min_documentation_chars} characters minimum.
              </p>
            </div>

            <div className="flex flex-col gap-1">
              <label htmlFor="reflection" className="font-mono text-xs uppercase tracking-widest text-ink-muted">
                Reflection
              </label>
              <textarea
                id="reflection"
                rows={5}
                maxLength={5000}
                value={reflection}
                disabled={!editable}
                onChange={(event) => setReflection(event.target.value)}
                className={AREA}
              />
              <p className="text-xs text-ink-muted">
                How did you use AI, what did you verify yourself, and what would you change? {reflection.trim().length} /{" "}
                {detail.min_reflection_chars} characters minimum.
              </p>
            </div>
          </div>

          {editable && (
            <div className="mt-5">
              {problems.length > 0 && (
                <div className="mb-3 text-sm text-ink-muted">
                  <p>Before you can submit:</p>
                  <ul className="mt-1 list-disc pl-5">
                    {problems.map((problem) => (
                      <li key={problem}>{problem}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="flex flex-wrap items-center gap-3">
                <Button variant="secondary" onClick={() => save.mutate()} disabled={busy}>
                  {save.isPending ? "Saving..." : "Save draft"}
                </Button>
                <Button onClick={() => submit.mutate()} disabled={busy || problems.length > 0}>
                  {submit.isPending ? "Submitting..." : status === "changes_requested" ? "Resubmit for review" : "Submit for review"}
                </Button>
                {save.isSuccess && !busy && <span className="text-sm text-ok">Draft saved.</span>}
                {saved && <span className="font-mono text-xs text-ink-muted">Last saved {new Date(saved.updated_at).toLocaleString()}</span>}
              </div>
              {save.isError && <ErrorNote error={save.error} />}
              {submit.isError && <ErrorNote error={submit.error} />}
            </div>
          )}
        </section>
      </article>

      <aside className="space-y-8 text-sm">
        <section aria-label="Status">
          <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Status</p>
          <p className="mt-2">
            <ProjectStatusTag status={status} />
          </p>
          {saved?.submitted_at && (
            <p className="mt-1 font-mono text-xs text-ink-muted">
              Submitted {new Date(saved.submitted_at).toLocaleDateString()}
            </p>
          )}
        </section>

        <section aria-label="Requirements">
          <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">
            Requirements ({progress.done}/{progress.total})
          </p>
          <ul className="mt-2 space-y-2">
            {detail.requirements.map((item) => (
              <li key={item.id}>
                <label className="flex cursor-pointer items-start gap-2">
                  <input
                    type="checkbox"
                    className="mt-1"
                    checked={Boolean(checks[item.id])}
                    disabled={!editable}
                    onChange={(event) => setChecks({ ...checks, [item.id]: event.target.checked })}
                  />
                  <span>{item.text}</span>
                </label>
              </li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-ink-muted">Tick a requirement only when you have met it. A reviewer checks your work.</p>
        </section>

        <ReviewHistory reviews={detail.reviews} />

        {detail.concepts.length > 0 && (
          <section aria-label="Concepts">
            <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Concepts</p>
            <ul className="mt-2 space-y-1">
              {detail.concepts.map((concept) => (
                <li key={concept.slug} className="grid grid-cols-[1.25rem_1fr] gap-1">
                  <span className="font-mono text-xs text-ink-muted">{concept.category}</span>
                  <span>{concept.name}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </aside>
    </div>
  );
}
