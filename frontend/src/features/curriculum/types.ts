export type LessonStatus = "published" | "planned";
export type ProgressStatus = "not_started" | "in_progress" | "completed";
export type CourseKind = "stage" | "track";

export interface Concept {
  slug: string;
  name: string;
  category: "A" | "B" | "C";
}

export interface LessonSummary {
  id: string;
  slug: string;
  title: string;
  summary: string;
  position: number;
  estimated_minutes: number;
  status: LessonStatus;
  principles: string[];
  progress: ProgressStatus;
}

export interface ModuleRead {
  id: string;
  slug: string;
  title: string;
  summary: string;
  position: number;
  status: LessonStatus;
  lessons: LessonSummary[];
}

export interface CourseSummary {
  id: string;
  slug: string;
  title: string;
  summary: string;
  kind: CourseKind;
  stage_number: number | null;
  position: number;
  module_count: number;
  published_lesson_count: number;
  planned_lesson_count: number;
  completed_lesson_count: number;
  enrolled: boolean;
}

export interface CourseDetail extends CourseSummary {
  modules: ModuleRead[];
}

export interface LessonLink {
  module_slug: string;
  slug: string;
  title: string;
}

export interface LessonProgress {
  status: ProgressStatus;
  time_spent_seconds: number;
  completed_at: string | null;
}

export interface LessonDetail {
  id: string;
  slug: string;
  title: string;
  summary: string;
  estimated_minutes: number;
  status: LessonStatus;
  objectives: string[];
  principles: string[];
  content_md: string | null;
  concepts: Concept[];
  course_slug: string;
  course_title: string;
  module_slug: string;
  module_title: string;
  progress: LessonProgress;
  previous: LessonLink | null;
  next: LessonLink | null;
}

export interface Enrollment {
  course_slug: string;
  enrolled_at: string;
}

export interface Competency {
  slug: string;
  name: string;
  category: "A" | "B" | "C";
  lessons_completed: number;
}

export interface UpNext {
  reason: "continue" | "start";
  course_slug: string;
  course_title: string;
  module_slug: string;
  lesson_slug: string;
  lesson_title: string;
}

export interface ProgressSummary {
  lessons_completed: number;
  time_spent_seconds: number;
  courses: CourseSummary[];
  competencies: Competency[];
  up_next: UpNext | null;
}
