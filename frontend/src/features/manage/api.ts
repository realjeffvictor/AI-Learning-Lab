import { authedRequest } from "../auth/session";
import type { Role } from "../auth/types";
import type { Enrollment } from "../curriculum/types";
import type {
  ConceptOption,
  ContentTree,
  ExerciseCreate,
  ExerciseEdit,
  ExerciseWrite,
  LessonEdit,
  LessonWrite,
  Overview,
  ProjectEdit,
  ProjectWrite,
  StudentDetail,
  StudentPage,
} from "./types";

const enc = encodeURIComponent;
const BASE = "/api/v1/manage";

export const fetchOverview = (signal?: AbortSignal) => authedRequest<Overview>(`${BASE}/overview`, { signal });

export function fetchStudents(page: number, pageSize: number, q: string, role: Role | "", signal?: AbortSignal) {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (q.trim()) params.set("q", q.trim());
  if (role) params.set("role", role);
  return authedRequest<StudentPage>(`${BASE}/students?${params.toString()}`, { signal });
}

export const fetchStudent = (id: string, signal?: AbortSignal) =>
  authedRequest<StudentDetail>(`${BASE}/students/${enc(id)}`, { signal });

export const enrollStudent = (userId: string, course: string) =>
  authedRequest<Enrollment>(`${BASE}/students/${enc(userId)}/enrollments/${enc(course)}`, { method: "PUT" });

export const unenrollStudent = (userId: string, course: string) =>
  authedRequest<void>(`${BASE}/students/${enc(userId)}/enrollments/${enc(course)}`, { method: "DELETE" });

export const fetchContentTree = (signal?: AbortSignal) => authedRequest<ContentTree>(`${BASE}/content`, { signal });
export const fetchConcepts = (signal?: AbortSignal) => authedRequest<ConceptOption[]>(`${BASE}/concepts`, { signal });

export const fetchLessonEdit = (id: string, signal?: AbortSignal) =>
  authedRequest<LessonEdit>(`${BASE}/lessons/${enc(id)}`, { signal });
export const createLesson = (moduleId: string, body: LessonWrite & { slug: string }) =>
  authedRequest<LessonEdit>(`${BASE}/modules/${enc(moduleId)}/lessons`, { method: "POST", body });
export const updateLesson = (id: string, body: LessonWrite) =>
  authedRequest<LessonEdit>(`${BASE}/lessons/${enc(id)}`, { method: "PUT", body });

export const fetchManageExercises = (lessonId: string, signal?: AbortSignal) =>
  authedRequest<ExerciseEdit[]>(`${BASE}/lessons/${enc(lessonId)}/exercises`, { signal });
export const fetchExerciseEdit = (id: string, signal?: AbortSignal) =>
  authedRequest<ExerciseEdit>(`${BASE}/exercises/${enc(id)}`, { signal });
export const createExercise = (lessonId: string, body: ExerciseCreate) =>
  authedRequest<ExerciseEdit>(`${BASE}/lessons/${enc(lessonId)}/exercises`, { method: "POST", body });
export const updateExercise = (id: string, body: ExerciseWrite) =>
  authedRequest<ExerciseEdit>(`${BASE}/exercises/${enc(id)}`, { method: "PUT", body });
export const deleteExercise = (id: string) => authedRequest<void>(`${BASE}/exercises/${enc(id)}`, { method: "DELETE" });

export const fetchProjectEdit = (id: string, signal?: AbortSignal) =>
  authedRequest<ProjectEdit>(`${BASE}/projects/${enc(id)}`, { signal });
export const updateProject = (id: string, body: ProjectWrite) =>
  authedRequest<ProjectEdit>(`${BASE}/projects/${enc(id)}`, { method: "PUT", body });
