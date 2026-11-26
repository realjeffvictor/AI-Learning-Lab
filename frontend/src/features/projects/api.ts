import { authedRequest } from "../auth/session";
import type {
  Achievement,
  ProjectDetail,
  ProjectSummary,
  QueuePage,
  ReviewDetail,
  ReviewPayload,
  SubmissionDraft,
  SubmissionRead,
} from "./types";

const enc = encodeURIComponent;

export const fetchProjects = (signal?: AbortSignal) => authedRequest<ProjectSummary[]>("/api/v1/projects", { signal });

export const fetchProject = (course: string, slug: string, signal?: AbortSignal) =>
  authedRequest<ProjectDetail>(`/api/v1/projects/${enc(course)}/${enc(slug)}`, { signal });

export const saveDraft = (projectId: string, draft: SubmissionDraft) =>
  authedRequest<SubmissionRead>(`/api/v1/projects/${enc(projectId)}/submission`, { method: "PUT", body: draft });

export const submitProject = (projectId: string) =>
  authedRequest<SubmissionRead>(`/api/v1/projects/${enc(projectId)}/submission/submit`, { method: "POST" });

export const fetchQueue = (page: number, pageSize: number, signal?: AbortSignal) =>
  authedRequest<QueuePage>(`/api/v1/reviews/queue?page=${page}&page_size=${pageSize}`, { signal });

export const fetchReviewDetail = (submissionId: string, signal?: AbortSignal) =>
  authedRequest<ReviewDetail>(`/api/v1/reviews/submissions/${enc(submissionId)}`, { signal });

export const postReview = (submissionId: string, payload: ReviewPayload) =>
  authedRequest<ReviewDetail>(`/api/v1/reviews/submissions/${enc(submissionId)}`, { method: "POST", body: payload });

export const fetchAchievements = (signal?: AbortSignal) =>
  authedRequest<Achievement[]>("/api/v1/achievements", { signal });
