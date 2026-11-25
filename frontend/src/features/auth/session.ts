import { apiRequest, type RequestOptions } from "../../lib/api/client";
import { ApiError } from "../../lib/api/errors";
import type { TokenResponse } from "./types";

// The access token lives in memory only: it never touches localStorage, so an XSS bug cannot read it
// from storage. The refresh token is an HttpOnly cookie that JavaScript cannot see at all.
let accessToken: string | null = null;
let refreshInFlight: Promise<TokenResponse> | null = null;
let onSessionExpired: (() => void) | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function setSessionExpiredHandler(handler: (() => void) | null): void {
  onSessionExpired = handler;
}

/** Single-flight: concurrent callers (React StrictMode, parallel requests) share one refresh,
 *  because a second rotation of the same token would look like token theft to the server. */
export function refreshSession(): Promise<TokenResponse> {
  if (!refreshInFlight) {
    refreshInFlight = apiRequest<TokenResponse>("/api/v1/auth/refresh", { method: "POST", csrf: true })
      .then((result) => {
        accessToken = result.access_token;
        return result;
      })
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
}

/** Authenticated request. On a 401 it refreshes the session once and retries. */
export async function authedRequest<T>(
  path: string,
  options: Omit<RequestOptions, "token" | "csrf"> = {},
): Promise<T> {
  try {
    return await apiRequest<T>(path, { ...options, token: accessToken });
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== 401) throw error;
  }
  try {
    await refreshSession();
  } catch (refreshError) {
    accessToken = null;
    onSessionExpired?.();
    throw refreshError;
  }
  return apiRequest<T>(path, { ...options, token: accessToken });
}
