import type { Role, User } from "../auth/types";
import type { CourseSummary } from "../curriculum/types";
import type { ExerciseKind, Mastery } from "../exercises/types";
import type { ProjectKind, ProjectSummary, Requirement } from "../projects/types";

export interface EnrollmentCount {
  course_slug: string;
  course_title: string;
  enrolled: number;
}
export interface LessonCompletion {
  course_slug: string;
  module_slug: string;
  lesson_slug: string;
  title: string;
  completed: number;
}
export interface ExerciseStat {
  exercise_id: string;
  title: string;
  kind: ExerciseKind;
  lesson_title: string;
  attempts: number;
  learners: number;
  passed_learners: number;
}
export interface Overview {
  users_by_role: Record<string, number>;
  active_learners_7d: number;
  pending_reviews: number;
  enrollments: EnrollmentCount[];
  top_lessons: LessonCompletion[];
  exercises: ExerciseStat[];
  ai: { requests_today: number; requests_7d: number; tokens_7d: number };
}

export interface StudentRow {
  id: string;
  email: string;
  display_name: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  lessons_completed: number;
  enrollments: number;
  last_active_at: string | null;
}
export interface StudentPage {
  items: StudentRow[];
  page: number;
  page_size: number;
  total: number;
}
export interface StudentDetail {
  user: User;
  lessons_completed: number;
  time_spent_seconds: number;
  exercise_attempts: number;
  exercises_passed: number;
  courses: CourseSummary[];
  projects: ProjectSummary[];
  mastery: Mastery[];
}

export interface ContentLesson {
  id: string;
  slug: string;
  title: string;
  status: "published" | "planned";
  managed_in_app: boolean;
  exercise_count: number;
}
export interface ContentModule {
  id: string;
  slug: string;
  title: string;
  lessons: ContentLesson[];
}
export interface ContentProject {
  id: string;
  slug: string;
  title: string;
  kind: ProjectKind;
  managed_in_app: boolean;
}
export interface ContentCourse {
  id: string;
  slug: string;
  title: string;
  kind: "stage" | "track";
  modules: ContentModule[];
  projects: ContentProject[];
}
export interface ContentTree {
  courses: ContentCourse[];
}
export interface ConceptOption {
  slug: string;
  name: string;
  category: "A" | "B" | "C";
}

export interface LessonWrite {
  title: string;
  summary: string;
  minutes: number;
  objectives: string[];
  principles: string[];
  concepts: string[];
  content_md: string | null;
}
export interface LessonEdit extends LessonWrite {
  id: string;
  slug: string;
  status: "published" | "planned";
  module_id: string;
  module_slug: string;
  module_title: string;
  course_slug: string;
  course_title: string;
  managed_in_app: boolean;
}

export interface ExerciseWrite {
  title: string;
  instructions_md: string;
  pass_score: number;
  concepts: string[];
  definition: Record<string, unknown>;
}
export interface ExerciseCreate extends ExerciseWrite {
  slug: string;
  kind: ExerciseKind;
}
export interface ExerciseEdit extends ExerciseWrite {
  id: string;
  lesson_id: string;
  lesson_title: string;
  slug: string;
  kind: ExerciseKind;
  attempts: number;
  managed_in_app: boolean;
}

export interface ProjectWrite {
  title: string;
  summary: string;
  brief_md: string;
}
export interface ProjectEdit extends ProjectWrite {
  id: string;
  slug: string;
  kind: ProjectKind;
  course_slug: string;
  course_title: string;
  requirements: Requirement[];
  managed_in_app: boolean;
}
