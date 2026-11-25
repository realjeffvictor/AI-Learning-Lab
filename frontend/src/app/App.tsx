import { Route, Routes } from "react-router-dom";

import { AppShell } from "../features/auth/AppShell";
import { RequireAuth } from "../features/auth/RequireAuth";
import { AdminUsersPage } from "../routes/AdminUsersPage";
import { CourseDetailPage } from "../routes/CourseDetailPage";
import { CoursesPage } from "../routes/CoursesPage";
import { DashboardPage } from "../routes/DashboardPage";
import { HomePage } from "../routes/HomePage";
import { LessonPage } from "../routes/LessonPage";
import { LoginPage } from "../routes/LoginPage";
import { ModulePage } from "../routes/ModulePage";
import { NotFoundPage } from "../routes/NotFoundPage";
import { ProfilePage } from "../routes/ProfilePage";
import { ProgressPage } from "../routes/ProgressPage";
import { RegisterPage } from "../routes/RegisterPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
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
        <Route path="/progress" element={<ProgressPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route element={<RequireAuth roles={["admin"]} />}>
          <Route path="/admin/users" element={<AdminUsersPage />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
