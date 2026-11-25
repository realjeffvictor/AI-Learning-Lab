import { ApiError } from "./errors";

/** Turns any thrown value into a sentence that is safe to show a user. */
export function describeError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.code === "validation_error") {
      const first = error.details[0] as { msg?: unknown } | undefined;
      if (first && typeof first.msg === "string") return first.msg.replace(/^Value error, /, "");
    }
    return error.message;
  }
  return "Something went wrong. Please try again.";
}
