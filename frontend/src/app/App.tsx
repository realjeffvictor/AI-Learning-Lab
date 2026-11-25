import { Route, Routes } from "react-router-dom";

import { AppShell } from "../features/auth/AppShell";
import { RequireAuth } from "../features/auth/RequireAuth";
import { AdminUsersPage } from "../routes/AdminUsersPage";
import { DashboardPage } from "../routes/DashboardPage";
import { HomePage } from "../routes/HomePage";
import { LoginPage } from "../routes/LoginPage";
import { NotFoundPage } from "../routes/NotFoundPage";
import { ProfilePage } from "../routes/ProfilePage";
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
        <Route path="/profile" element={<ProfilePage />} />
        <Route element={<RequireAuth roles={["admin"]} />}>
          <Route path="/admin/users" element={<AdminUsersPage />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
