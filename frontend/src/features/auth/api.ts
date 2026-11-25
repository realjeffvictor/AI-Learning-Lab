import { apiRequest } from "../../lib/api/client";
import { authedRequest, setAccessToken } from "./session";
import type { ExperienceLevel, Role, TokenResponse, User, UserPage } from "./types";

export interface ProfileChanges {
  display_name?: string;
  bio?: string | null;
  experience_level?: ExperienceLevel;
}

export interface UserChanges {
  role?: Role;
  is_active?: boolean;
}

export async function login(email: string, password: string): Promise<User> {
  const result = await apiRequest<TokenResponse>("/api/v1/auth/login", { method: "POST", body: { email, password } });
  setAccessToken(result.access_token);
  return result.user;
}

export async function register(email: string, password: string, displayName: string): Promise<User> {
  const result = await apiRequest<TokenResponse>("/api/v1/auth/register", {
    method: "POST",
    body: { email, password, display_name: displayName },
  });
  setAccessToken(result.access_token);
  return result.user;
}

export async function logout(): Promise<void> {
  try {
    await apiRequest<void>("/api/v1/auth/logout", { method: "POST", csrf: true });
  } finally {
    setAccessToken(null);
  }
}

export function updateProfile(changes: ProfileChanges): Promise<User> {
  return authedRequest<User>("/api/v1/users/me/profile", { method: "PATCH", body: changes });
}

export function listUsers(page: number, pageSize: number, signal?: AbortSignal): Promise<UserPage> {
  return authedRequest<UserPage>(`/api/v1/users?page=${page}&page_size=${pageSize}`, { signal });
}

export function updateUser(id: string, changes: UserChanges): Promise<User> {
  return authedRequest<User>(`/api/v1/users/${id}`, { method: "PATCH", body: changes });
}
