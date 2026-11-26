import { authedRequest } from "../auth/session";
import type { ExercisePublic, Mastery, SubmissionResult, SubmissionSummary } from "./types";

const enc = encodeURIComponent;

export const fetchExercises = (lessonId: string, signal?: AbortSignal) =>
  authedRequest<ExercisePublic[]>(`/api/v1/lessons/${enc(lessonId)}/exercises`, { signal });

export const submitExercise = (exerciseId: string, answer: Record<string, unknown>) =>
  authedRequest<SubmissionResult>(`/api/v1/exercises/${enc(exerciseId)}/submissions`, {
    method: "POST",
    body: { answer },
  });

export const fetchHistory = (exerciseId: string, signal?: AbortSignal) =>
  authedRequest<SubmissionSummary[]>(`/api/v1/exercises/${enc(exerciseId)}/submissions`, { signal });

export const fetchMastery = (signal?: AbortSignal) => authedRequest<Mastery[]>("/api/v1/assessments/mastery", { signal });
