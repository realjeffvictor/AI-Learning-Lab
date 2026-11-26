import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button } from "../components/Button";
import { ErrorNote, Loading } from "../components/StateMessage";
import { fetchNotifications, markAllRead, markRead } from "../features/notifications/api";

export function NotificationsPage() {
  const queryClient = useQueryClient();
  const notifications = useQuery({ queryKey: ["notifications", "list"], queryFn: ({ signal }) => fetchNotifications(signal) });
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["notifications"] });
  const readOne = useMutation({ mutationFn: markRead, onSuccess: refresh });
  const readAll = useMutation({ mutationFn: markAllRead, onSuccess: refresh });

  if (notifications.isPending) return <Loading label="Loading notifications" />;
  if (notifications.isError) return <ErrorNote error={notifications.error} />;
  const data = notifications.data;

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-widest text-ink-muted">Notifications</p>
      <div className="mt-2 flex flex-wrap items-baseline gap-4">
        <h1 className="font-serif text-3xl">Notifications</h1>
        <Button variant="secondary" disabled={data.unread_count === 0 || readAll.isPending} onClick={() => readAll.mutate()}>
          Mark all read
        </Button>
      </div>
      {data.items.length === 0 ? (
        <p className="mt-8 text-ink-muted">Nothing yet. You will be told here when a project is reviewed or you are enrolled in a course.</p>
      ) : (
        <ul className="mt-8 max-w-3xl divide-y divide-rule border-y border-rule">
          {data.items.map((item) => (
            <li key={item.id} className="py-3">
              <p className={item.read_at ? "text-ink-muted" : "font-medium"}>
                {item.link ? (
                  <Link to={item.link} onClick={() => !item.read_at && readOne.mutate(item.id)} className="hover:text-signal">
                    {item.title}
                  </Link>
                ) : (
                  item.title
                )}
              </p>
              {item.body && <p className="text-sm text-ink-muted">{item.body}</p>}
              <p className="mt-1 font-mono text-xs text-ink-muted">
                {new Date(item.created_at).toLocaleString()}
                {!item.read_at && (
                  <button type="button" className="ml-3 text-signal underline underline-offset-4" onClick={() => readOne.mutate(item.id)}>
                    Mark read
                  </button>
                )}
              </p>
            </li>
          ))}
        </ul>
      )}
      {(readOne.isError || readAll.isError) && <ErrorNote error={readOne.error ?? readAll.error} />}
    </div>
  );
}
