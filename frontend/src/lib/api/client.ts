import { ApiError } from "./errors";

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "";

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method: "GET",
      headers: { Accept: "application/json" },
      signal,
    });
  } catch (cause) {
    if (cause instanceof DOMException && cause.name === "AbortError") throw cause;
    throw new ApiError({
      status: 0,
      code: "network_error",
      message: "Cannot reach the API server.",
      requestId: null,
    });
  }
  if (!response.ok) throw await ApiError.fromResponse(response);
  return (await response.json()) as T;
}
