import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { Button } from "../components/Button";
import { ErrorNote, Loading } from "../components/StateMessage";
import { LessonMarkdown } from "../features/curriculum/LessonMarkdown";
import { fetchReviewDetail, postReview } from "../features/projects/api";
import { ProjectStatusTag } from "../features/projects/ProjectStatusTag";
import { RUBRIC, SCORE_LABEL, type Outcome, type RubricCriterion } from "../features/projects/types";
import { KIND_LABEL, isGithubRepo } from "../features/projects/utils";

const FIELD = "rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink";

export function ReviewDetailPage() {
  const { submissionId } = useParams();
  const queryClient = useQueryClient();
  const detail = useQuery({
    queryKey: ["reviews", "detail", submissionId],
    queryFn: ({ signal }) => fetchReviewDetail(submissionId as string, signal),
    enabled: Boolean(submissionId),
  });

  const [scores, setScores] = useState<Partial<Record<RubricCriterion, number>>>({});
  const [feedback, setFeedback] = useState("");

  const review = useMutation({
    mutationFn: (outcome: Outcome) =>
      postReview(submissionId as string, {
        outcome,
        rubric_scores: scores as Record<RubricCriterion, number>,
        feedback,
      }),
    onSuccess: (updated) => {
      queryClient.setQueryData(["reviews", "detail", submissionId], updated);
      void queryClient.invalidateQueries({ queryKey: ["reviews", "queue"] });
      setScores({});
      setFeedback("");
    },
  });

  if (detail.isPending) return <Loading label="Loading submission" />;
  if (detail.isError) return <ErrorNote error={detail.error} />;
  const data = detail.data;
  const status = data.submission.status;
  const complete = RUBRIC.every((item) => scores[item.key] !== undefined) && feedback.trim().length >= 10;
  const lowest = Math.min(...RUBRIC.map((item) => scores[item.key] ?? 4));
  const canApprove = complete && lowest >= 2;

  return (
    <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_22rem]">
      <article>
        <nav aria-label="Breadcrumb" className="font-mono text-xs text-ink-muted">
          <Link to="/reviews" className="hover:text-ink">
            Reviews
          </Link>{" "}
          / {data.project_title}
        </nav>
        <p className="mt-3 font-mono text-xs uppercase tracking-widest text-signal">{KIND_LABEL[data.project_kind]}</p>
        <h1 className="mt-1 font-serif text-3xl">{data.project_title}</h1>
        <p className="mt-1 font-mono text-xs text-ink-muted">
          {data.learner_name} ({data.learner_email}). <ProjectStatusTag status={status} />
        </p>

        <section className="mt-6" aria-label="Repository">
          <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Repository</p>
          {isGithubRepo(data.submission.repo_url) ? (
            <a
              href={data.submission.repo_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 inline-block text-signal underline underline-offset-4"
            >
              {data.submission.repo_url}
            </a>
          ) : (
            <p className="mt-1 text-sm text-ink-muted">{data.submission.repo_url ?? "No repository for this project."}</p>
          )}
          <p className="mt-1 text-xs text-ink-muted">The link is not checked by the platform. Open it and confirm it is public and matches the work.</p>
        </section>

        <section className="mt-8" aria-label="Documentation">
          <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Documentation</p>
          <div className="mt-2 border-l-2 border-rule pl-4">
            <LessonMarkdown source={data.submission.documentation_md || "(empty)"} />
          </div>
        </section>

        <section className="mt-8" aria-label="Reflection">
          <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Reflection</p>
          <div className="mt-2 border-l-2 border-rule pl-4">
            <LessonMarkdown source={data.submission.reflection_md || "(empty)"} />
          </div>
        </section>

        <details className="mt-8 border-t border-rule pt-4">
          <summary className="cursor-pointer font-mono text-xs uppercase tracking-widest text-ink-muted">Project brief</summary>
          <div className="mt-3">
            <LessonMarkdown source={data.brief_md} />
          </div>
        </details>
      </article>

      <aside className="space-y-8 text-sm">
        <section aria-label="Requirements">
          <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Learner ticked</p>
          <ul className="mt-2 space-y-1">
            {data.requirements.map((item) => (
              <li key={item.id} className="grid grid-cols-[1.25rem_1fr] gap-1">
                <span className={data.submission.requirement_checks[item.id] ? "text-ok" : "text-warn"}>
                  {data.submission.requirement_checks[item.id] ? "+" : "-"}
                </span>
                <span>{item.text}</span>
              </li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-ink-muted">These are the learner's own ticks. Verify them against the work.</p>
        </section>

        {status === "submitted" ? (
          <section aria-label="Your review">
            <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Your review</p>
            <div className="mt-3 flex flex-col gap-3">
              {RUBRIC.map((item) => (
                <div key={item.key} className="flex flex-col gap-1">
                  <label htmlFor={`score-${item.key}`}>{item.label}</label>
                  <select
                    id={`score-${item.key}`}
                    value={scores[item.key] ?? ""}
                    onChange={(event) =>
                      setScores({ ...scores, [item.key]: event.target.value === "" ? undefined : Number(event.target.value) })
                    }
                    className={FIELD}
                  >
                    <option value="">Choose a score</option>
                    {[1, 2, 3, 4].map((value) => (
                      <option key={value} value={value}>
                        {value} {SCORE_LABEL[value]}
                      </option>
                    ))}
                  </select>
                  <span className="text-xs text-ink-muted">{item.hint}</span>
                </div>
              ))}
              <div className="flex flex-col gap-1">
                <label htmlFor="feedback">Feedback for the learner</label>
                <textarea
                  id="feedback"
                  rows={6}
                  maxLength={4000}
                  value={feedback}
                  onChange={(event) => setFeedback(event.target.value)}
                  className={FIELD}
                />
              </div>
              <div className="flex flex-wrap gap-2">
                <Button onClick={() => review.mutate("approved")} disabled={!canApprove || review.isPending}>
                  Approve
                </Button>
                <Button variant="secondary" onClick={() => review.mutate("changes_requested")} disabled={!complete || review.isPending}>
                  Request changes
                </Button>
              </div>
              {complete && !canApprove && (
                <p className="text-xs text-ink-muted">Approval needs a score of at least 2 on every criterion.</p>
              )}
              {review.isError && <ErrorNote error={review.error} />}
            </div>
          </section>
        ) : (
          <p className="text-ink-muted">This submission is not awaiting review.</p>
        )}

        {data.reviews.length > 0 && (
          <section aria-label="Earlier reviews">
            <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Review history</p>
            <ol className="mt-2 space-y-3">
              {data.reviews.map((item) => (
                <li key={item.id} className="border-l-2 border-rule pl-3">
                  <p className={item.outcome === "approved" ? "text-ok" : "text-warn"}>
                    {item.outcome === "approved" ? "Approved" : "Changes requested"}
                    <span className="text-ink-muted">
                      {" "}
                      by {item.reviewer_name ?? "a reviewer"}, {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </p>
                  <p className="mt-1 whitespace-pre-wrap">{item.feedback}</p>
                </li>
              ))}
            </ol>
          </section>
        )}
      </aside>
    </div>
  );
}
