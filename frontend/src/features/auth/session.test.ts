import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "../../lib/api/errors";
import { authedRequest, refreshSession, setAccessToken, setSessionExpiredHandler } from "./session";

const tokenBody = { access_token: "new-token", token_type: "bearer", expires_in: 900, user: {} };

function envelope(status: number, code: string): Response {
  const body = { error: { code, message: "nope", details: [], request_id: "req-12345678" } };
  return new Response(JSON.stringify(body), { status });
}

afterEach(() => {
  vi.unstubAllGlobals();
  setAccessToken(null);
  setSessionExpiredHandler(null);
});

describe("session", () => {
  it("shares one refresh request between concurrent callers", async () => {
    const fetchMock = vi.fn().mockImplementation(async () => new Response(JSON.stringify(tokenBody), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    await Promise.all([refreshSession(), refreshSession()]);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("refreshes once on 401 and retries with the new token", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(envelope(401, "invalid_token"))
      .mockResolvedValueOnce(new Response(JSON.stringify(tokenBody), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ok: true }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(authedRequest<{ ok: boolean }>("/api/v1/users/me")).resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(String(fetchMock.mock.calls[1][0])).toContain("/auth/refresh");
    const retryHeaders = fetchMock.mock.calls[2][1].headers as Record<string, string>;
    expect(retryHeaders.Authorization).toBe("Bearer new-token");
  });

  it("signals session expiry when the refresh itself fails", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(envelope(401, "invalid_token"))
      .mockResolvedValueOnce(envelope(401, "invalid_refresh_token"));
    vi.stubGlobal("fetch", fetchMock);
    const expired = vi.fn();
    setSessionExpiredHandler(expired);

    await expect(authedRequest("/api/v1/users/me")).rejects.toBeInstanceOf(ApiError);
    expect(expired).toHaveBeenCalledTimes(1);
  });
});
