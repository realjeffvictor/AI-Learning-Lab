import { Link, NavLink, Outlet } from "react-router-dom";

import { Button } from "../../components/Button";
import { useAuth } from "./AuthContext";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `border-b-2 py-3 text-sm ${isActive ? "border-signal text-ink" : "border-transparent text-ink-muted hover:text-ink"}`;

export function AppShell() {
  const { user, logout } = useAuth();
  if (!user) return null;
  return (
    <div className="min-h-screen">
      <header className="border-b border-rule bg-surface">
        <div className="mx-auto flex max-w-[1200px] flex-wrap items-center gap-x-6 gap-y-1 px-6">
          <Link to="/dashboard" className="py-3 font-serif text-lg">
            AI Learning Lab
          </Link>
          <nav aria-label="Main" className="flex flex-wrap gap-5">
            <NavLink to="/dashboard" className={linkClass}>
              Dashboard
            </NavLink>
            <NavLink to="/courses" className={linkClass}>
              Curriculum
            </NavLink>
            <NavLink to="/progress" className={linkClass}>
              Progress
            </NavLink>
            <NavLink to="/profile" className={linkClass}>
              Profile
            </NavLink>
            {user.role === "admin" && (
              <NavLink to="/admin/users" className={linkClass}>
                Users
              </NavLink>
            )}
          </nav>
          <div className="ml-auto flex items-center gap-3 py-2 text-sm">
            <span className="font-mono text-xs uppercase tracking-widest text-ink-muted">{user.role}</span>
            <span>{user.profile.display_name}</span>
            <Button variant="secondary" onClick={() => void logout()}>
              Sign out
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-[1200px] px-6 py-10">
        <Outlet />
      </main>
    </div>
  );
}
