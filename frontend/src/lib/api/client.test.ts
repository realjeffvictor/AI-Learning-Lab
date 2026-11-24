import { afterEach, describe, expect, it, vi } from "vitest";

import { apiGet } from "./client";
import { ApiError } from "./errors";

afterEach(() => {
  vi.unstubAllGlobals();
});

function stubFetch(response: Response) {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response));
}

describe("apiGet", () => {
  it("returns parsed JSON on success", async () => {
    stubFetch(new Response(JSON.stringify({ status: "ok" }), { status: 200 }));
    await expect(apiGet("/api/v1/health")).resolves.toEqual({ status: "ok" });
  });

  it("maps the backend error envelope to ApiError", async () => {
    const body = { error: { code: "not_found", message: "Nope", details: [], request_id: "req-12345678" } };
    stubFetch(new Response(JSON.stringify(body), { status: 404 }));
    const error = await apiGet("/x").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 404, code: "not_found", message: "Nope", requestId: "req-12345678" });
  });

  it("falls back when the error body is not JSON", async () => {
    stubFetch(new Response("<html>bad gateway</html>", { status: 502 }));
    const error = await apiGet("/x").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 502, code: "http_502" });
  });

  it("reports network failures as network_error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    await expect(apiGet("/x")).rejects.toMatchObject({ code: "network_error", status: 0 });
  });
});
