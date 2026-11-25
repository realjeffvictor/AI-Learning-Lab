import { useAuth } from "../features/auth/AuthContext";

function formatDate(iso: string | null): string {
  return iso ? new Date(iso).toLocaleString() : "never";
}

export function DashboardPage() {
  const { user } = useAuth();
  if (!user) return null;

  const rows: [string, string][] = [
    ["Email", user.email],
    ["Role", user.role],
    ["Experience", user.profile.experience_level],
    ["Member since", formatDate(user.created_at)],
    ["Last sign-in", formatDate(user.last_login_at)],
  ];

  return (
    <div className="grid gap-12 lg:grid-cols-[minmax(0,1fr)_22rem]">
      <section>
        <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Dashboard</p>
        <h1 className="mt-2 font-serif text-3xl">Welcome, {user.profile.display_name}</h1>
        <p className="mt-4 max-w-xl text-ink-muted">
          Your account is ready. Courses, lessons and the Python playground arrive in the next phases, so there is
          nothing to start yet.
        </p>
      </section>
      <section aria-labelledby="account-heading">
        <h2 id="account-heading" className="mb-3 font-mono text-xs uppercase tracking-widest text-ink-muted">
          Account
        </h2>
        <dl className="divide-y divide-rule border-y border-rule font-mono text-sm">
          {rows.map(([label, value]) => (
            <div key={label} className="grid grid-cols-[8rem_1fr] gap-2 py-2">
              <dt className="text-ink-muted">{label}</dt>
              <dd className="break-all">{value}</dd>
            </div>
          ))}
        </dl>
      </section>
    </div>
  );
}
