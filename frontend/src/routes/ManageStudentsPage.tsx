import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { Button } from "../components/Button";
import { ErrorNote, Loading } from "../components/StateMessage";
import type { Role } from "../features/auth/types";
import { fetchStudents } from "../features/manage/api";

const PAGE_SIZE = 20;
const FIELD = "rounded-md border border-rule bg-surface px-3 py-2 text-base text-ink";

export function ManageStudentsPage() {
  const [input, setInput] = useState("");
  const [q, setQ] = useState("");
  const [role, setRole] = useState<Role | "">("");
  const [page, setPage] = useState(1);
  const students = useQuery({
    queryKey: ["manage", "students", q, role, page],
    queryFn: ({ signal }) => fetchStudents(page, PAGE_SIZE, q, role, signal),
    placeholderData: keepPreviousData,
  });

  function onSearch(event: FormEvent) {
    event.preventDefault();
    setPage(1);
    setQ(input);
  }

  const totalPages = students.data ? Math.max(1, Math.ceil(students.data.total / students.data.page_size)) : 1;

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Manage</p>
      <h1 className="mt-2 font-serif text-3xl">Students</h1>
      <form onSubmit={onSearch} className="mt-6 flex flex-wrap items-end gap-3" role="search">
        <div className="flex flex-col gap-1">
          <label htmlFor="q" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Name or email</label>
          <input id="q" value={input} maxLength={100} onChange={(event) => setInput(event.target.value)} className={FIELD} />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="role" className="font-mono text-xs uppercase tracking-widest text-ink-muted">Role</label>
          <select
            id="role"
            value={role}
            onChange={(event) => {
              setRole(event.target.value as Role | "");
              setPage(1);
            }}
            className={FIELD}
          >
            <option value="">All</option>
            <option value="student">Students</option>
            <option value="instructor">Instructors</option>
            <option value="admin">Admins</option>
          </select>
        </div>
        <Button type="submit">Search</Button>
      </form>

      {students.isPending && <div className="mt-6"><Loading label="Loading" /></div>}
      {students.isError && <div className="mt-6"><ErrorNote error={students.error} /></div>}
      {students.data && (
        <>
          <div className="mt-6 overflow-x-auto">
            <table className="w-full min-w-[42rem] text-left text-sm">
              <thead className="border-y border-rule font-mono text-xs uppercase tracking-widest text-ink-muted">
                <tr>
                  <th className="py-2 pr-3 font-normal">Name</th>
                  <th className="py-2 pr-3 font-normal">Role</th>
                  <th className="py-2 pr-3 font-normal">Lessons done</th>
                  <th className="py-2 pr-3 font-normal">Courses</th>
                  <th className="py-2 font-normal">Last active</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-rule border-b border-rule">
                {students.data.items.map((row) => (
                  <tr key={row.id}>
                    <td className="py-2 pr-3">
                      <Link to={`/manage/students/${row.id}`} className="hover:text-signal">{row.display_name}</Link>
                      <span className="block font-mono text-xs text-ink-muted">{row.email}{row.is_active ? "" : " (deactivated)"}</span>
                    </td>
                    <td className="py-2 pr-3 font-mono text-xs">{row.role}</td>
                    <td className="py-2 pr-3 font-mono">{row.lessons_completed}</td>
                    <td className="py-2 pr-3 font-mono">{row.enrollments}</td>
                    <td className="py-2 text-ink-muted">{row.last_active_at ? new Date(row.last_active_at).toLocaleDateString() : "never"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {students.data.items.length === 0 && <p className="mt-4 text-ink-muted">No one matches.</p>}
          <div className="mt-4 flex items-center gap-3 text-sm">
            <Button variant="secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</Button>
            <span className="font-mono text-ink-muted">{page} / {totalPages}</span>
            <Button variant="secondary" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</Button>
            <span className="ml-auto text-ink-muted">{students.data.total} people</span>
          </div>
        </>
      )}
    </div>
  );
}
