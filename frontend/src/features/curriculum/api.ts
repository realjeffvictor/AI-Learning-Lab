import { authedRequest } from "../auth/session";
import type {
  CourseDetail,
  CourseSummary,
  Enrollment,
  LessonDetail,
  LessonProgress,
  ProgressSummary,
} from "./types";

const enc = encodeURIComponent;

export const fetchCourses = (signal?: AbortSignal) => authedRequest<CourseSummary[]>("/api/v1/courses", { signal });

export const fetchCourse = (slug: string, signal?: AbortSignal) =>
  authedRequest<CourseDetail>(`/api/v1/courses/${enc(slug)}`, { signal });

export const fetchLesson = (course: string, module: string, lesson: string, signal?: AbortSignal) =>
  authedRequest<LessonDetail>(`/api/v1/courses/${enc(course)}/modules/${enc(module)}/lessons/${enc(lesson)}`, {
    signal,
  });

export const enrollInCourse = (slug: string) =>
  authedRequest<Enrollment>(`/api/v1/courses/${enc(slug)}/enrollment`, { method: "POST" });

export const fetchProgressSummary = (signal?: AbortSignal) =>
  authedRequest<ProgressSummary>("/api/v1/progress/summary", { signal });

export const startLesson = (lessonId: string) =>
  authedRequest<LessonProgress>(`/api/v1/progress/lessons/${enc(lessonId)}/start`, { method: "POST" });

export const addLessonTime = (lessonId: string, seconds: number) =>
  authedRequest<LessonProgress>(`/api/v1/progress/lessons/${enc(lessonId)}/time`, {
    method: "POST",
    body: { seconds },
  });

export const completeLesson = (lessonId: string) =>
  authedRequest<LessonProgress>(`/api/v1/progress/lessons/${enc(lessonId)}/complete`, { method: "POST" });
