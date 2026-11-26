import { authedRequest } from "../auth/session";

export interface NotificationItem {
  id: string;
  kind: string;
  title: string;
  body: string;
  link: string | null;
  read_at: string | null;
  created_at: string;
}

export interface NotificationList {
  items: NotificationItem[];
  unread_count: number;
}

const enc = encodeURIComponent;

export const fetchNotifications = (signal?: AbortSignal) =>
  authedRequest<NotificationList>("/api/v1/notifications", { signal });

export const fetchUnreadCount = (signal?: AbortSignal) =>
  authedRequest<{ unread_count: number }>("/api/v1/notifications/unread-count", { signal });

export const markRead = (id: string) =>
  authedRequest<void>(`/api/v1/notifications/${enc(id)}/read`, { method: "POST" });

export const markAllRead = () => authedRequest<void>("/api/v1/notifications/read-all", { method: "POST" });
