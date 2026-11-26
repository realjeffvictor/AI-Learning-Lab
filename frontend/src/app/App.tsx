import { Route, Routes } from "react-router-dom";

import { AppShell } from "../features/auth/AppShell";
import { RequireAuth } from "../features/auth/RequireAuth";
import { AdminUsersPage } from "../routes/AdminUsersPage";
import { AssistantPage } from "../routes/AssistantPage";
import { CourseDetailPage } from "../routes/CourseDetailPage";
import { CoursesPage } from "../routes/CoursesPage";
import { DashboardPage } from "../routes/DashboardPage";
import { ExerciseEditorPage } from "../routes/ExerciseEditorPage";
import { HomePage } from "../routes/HomePage";
import { LessonEditorPage } from "../routes/LessonEditorPage";
import { LessonPage } from "../routes/LessonPage";
import { LoginPage } from "../routes/LoginPage";
import { ManageContentPage } from "../routes/ManageContentPage";
import { ManageDashboardPage } from "../routes/ManageDashboardPage";
import { ManageStudentPage } from "../routes/ManageStudentPage";
import { ManageStudentsPage } from "../routes/ManageStudentsPage";
import { ModulePage } from "../routes/ModulePage";
import { NotFoundPage } from "../routes/NotFoundPage";
import { NotificationsPage } from "../routes/NotificationsPage";
import { PlaygroundPage } from "../routes/PlaygroundPage";
import { ProfilePage } from "../routes/ProfilePage";
import { ProgressPage } from "../routes/ProgressPage";
import { ProjectEditorPage } from "../routes/ProjectEditorPage";
import { ProjectPage } from "../routes/ProjectPage";
import { ProjectsPage } from "../routes/ProjectsPage";
import { RegisterPage } from "../routes/RegisterPage";
import { VerifyCertificatePage } from "../routes/VerifyCertificatePage";
import { ReviewDetailPage } from "../routes/ReviewDetailPage";
import { ReviewQueuePage } from "../routes/ReviewQueuePage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/verify/:code" element={<VerifyCertificatePage />} />
      <Route
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/courses" element={<CoursesPage />} />
        <Route path="/courses/:courseSlug" element={<CourseDetailPage />} />
        <Route path="/courses/:courseSlug/:moduleSlug" element={<ModulePage />} />
        <Route path="/courses/:courseSlug/:moduleSlug/:lessonSlug" element={<LessonPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/:courseSlug/:projectSlug" element={<ProjectPage />} />
        <Route path="/progress" element={<ProgressPage />} />
        <Route path="/playground" element={<PlaygroundPage />} />
        <Route path="/assistant" element={<AssistantPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route element={<RequireAuth roles={["instructor", "admin"]} />}>
          <Route path="/manage" element={<ManageDashboardPage />} />
          <Route path="/manage/students" element={<ManageStudentsPage />} />
          <Route path="/manage/students/:userId" element={<ManageStudentPage />} />
          <Route path="/manage/content" element={<ManageContentPage />} />
          <Route path="/manage/modules/:moduleId/lessons/new" element={<LessonEditorPage />} />
          <Route path="/manage/lessons/:lessonId" element={<LessonEditorPage />} />
          <Route path="/manage/lessons/:lessonId/exercises/new" element={<ExerciseEditorPage />} />
          <Route path="/manage/exercises/:exerciseId" element={<ExerciseEditorPage />} />
          <Route path="/manage/projects/:projectId" element={<ProjectEditorPage />} />
          <Route path="/reviews" element={<ReviewQueuePage />} />
          <Route path="/reviews/:submissionId" element={<ReviewDetailPage />} />
        </Route>
        <Route element={<RequireAuth roles={["admin"]} />}>
          <Route path="/admin/users" element={<AdminUsersPage />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
