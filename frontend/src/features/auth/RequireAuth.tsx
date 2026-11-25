import type { ReactNode } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "./AuthContext";
import type { Role } from "./types";

/** UX guard only. The backend enforces every permission independently. */
export function RequireAuth({ roles, children }: { roles?: Role[]; children?: ReactNode }) {
  const { status, user } = useAuth();
  const location = useLocation();

  if (status === "loading") {
    return <p className="p-8 font-mono text-sm text-ink-muted">Restoring session...</p>;
  }
  if (status === "anonymous" || !user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  if (roles && !roles.includes(user.role)) {
    return (
      <div className="py-12">
        <p className="font-mono text-sm text-ink-muted">403</p>
        <h1 className="mt-2 font-serif text-3xl">No access</h1>
        <p className="mt-2 text-ink-muted">Your role does not include this page.</p>
      </div>
    );
  }
  return <>{children ?? <Outlet />}</>;
}
