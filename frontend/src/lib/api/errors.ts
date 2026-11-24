export interface ApiErrorInit {
  status: number;
  code: string;
  message: string;
  requestId: string | null;
  details?: unknown[];
}

/** Every API failure reaches the UI as an ApiError, matching the backend error envelope. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly requestId: string | null;
  readonly details: unknown[];

  constructor(init: ApiErrorInit) {
    super(init.message);
    this.name = "ApiError";
    this.status = init.status;
    this.code = init.code;
    this.requestId = init.requestId;
    this.details = init.details ?? [];
  }

  static async fromResponse(response: Response): Promise<ApiError> {
    const fallback: ApiErrorInit = {
      status: response.status,
      code: `http_${response.status}`,
      message: response.statusText || "Request failed",
      requestId: response.headers.get("X-Request-ID"),
    };
    try {
      const body: unknown = await response.json();
      const error = (body as { error?: Record<string, unknown> } | null)?.error;
      if (error && typeof error === "object") {
        return new ApiError({
          status: response.status,
          code: typeof error.code === "string" ? error.code : fallback.code,
          message: typeof error.message === "string" ? error.message : fallback.message,
          requestId: typeof error.request_id === "string" ? error.request_id : fallback.requestId,
          details: Array.isArray(error.details) ? error.details : [],
        });
      }
    } catch {
      // The error body was not JSON; use the fallback below.
    }
    return new ApiError(fallback);
  }
}
