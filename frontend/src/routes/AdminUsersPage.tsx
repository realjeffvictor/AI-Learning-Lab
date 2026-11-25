import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "../components/Button";
import { listUsers, updateUser, type UserChanges } from "../features/auth/api";
import { useAuth } from "../features/auth/AuthContext";
import type { Role } from "../features/auth/types";
import { describeError } from "../lib/api/messages";

const ROLES: Role[] = ["student", "instructor", "admin"];
const PAGE_SIZE = 20;

export function AdminUsersPage() {
  const { user: me } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);

  const users = useQuery({
    queryKey: ["admin", "users", page],
    queryFn: ({ signal }) => listUsers(page, PAGE_SIZE, signal),
    placeholderData: keepPreviousData,
  });
  const change = useMutation({
    mutationFn: ({ id, changes }: { id: string; changes: UserChanges }) => updateUser(id, changes),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }),
  });

  const totalPages = users.data ? Math.max(1, Math.ceil(users.data.total / users.data.page_size)) : 1;

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Administration</p>
      <h1 className="mt-2 font-serif text-3xl">Users</h1>
      <p className="mt-2 text-ink-muted">Changes are enforced and audited by the server.</p>

      {users.isError && (
        <p role="alert" className="mt-6 text-sm text-danger">
          {describeError(users.error)}
        </p>
      )}
      {change.isError && (
        <p role="alert" className="mt-6 text-sm text-danger">
          {describeError(change.error)}
        </p>
      )}

      <div className="mt-8 overflow-x-auto">
        <table className="w-full min-w-[40rem] text-left text-sm">
          <thead className="border-y border-rule font-mono text-xs uppercase tracking-widest text-ink-muted">
            <tr>
              <th className="py-2 pr-4 font-normal">Email</th>
              <th className="py-2 pr-4 font-normal">Name</th>
              <th className="py-2 pr-4 font-normal">Role</th>
              <th className="py-2 pr-4 font-normal">Status</th>
              <th className="py-2 font-normal">Joined</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-rule border-b border-rule">
            {users.data?.items.map((row) => {
              const isMe = row.id === me?.id;
              return (
                <tr key={row.id}>
                  <td className="py-2 pr-4 font-mono">{row.email}</td>
                  <td className="py-2 pr-4">{row.profile.display_name}</td>
                  <td className="py-2 pr-4">
                    <select
                      aria-label={`Role for ${row.email}`}
                      value={row.role}
                      disabled={isMe || change.isPending}
                      onChange={(e) => change.mutate({ id: row.id, changes: { role: e.target.value as Role } })}
                      className="rounded-md border border-rule bg-surface px-2 py-1"
                    >
                      {ROLES.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="py-2 pr-4">
                    {isMe ? (
                      <span className="text-ink-muted">You</span>
                    ) : (
                      <Button
                        variant={row.is_active ? "danger" : "secondary"}
                        disabled={change.isPending}
                        onClick={() => change.mutate({ id: row.id, changes: { is_active: !row.is_active } })}
                      >
                        {row.is_active ? "Deactivate" : "Reactivate"}
                      </Button>
                    )}
                  </td>
                  <td className="py-2 text-ink-muted">{new Date(row.created_at).toLocaleDateString()}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center gap-3 text-sm">
        <Button variant="secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>
          Previous
        </Button>
        <span className="font-mono text-ink-muted">
          {page} / {totalPages}
        </span>
        <Button variant="secondary" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
          Next
        </Button>
        {users.data && <span className="ml-auto text-ink-muted">{users.data.total} users</span>}
      </div>
    </div>
  );
}
