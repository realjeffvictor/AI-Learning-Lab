import { apiGet } from "../../lib/api/client";

export interface HealthResponse {
  status: "ok";
  service: string;
  version: string;
  environment: string;
  timestamp: string;
}

export interface HealthCheckResult {
  health: HealthResponse;
  latencyMs: number;
}

export async function fetchHealth(signal?: AbortSignal): Promise<HealthCheckResult> {
  const start = performance.now();
  const health = await apiGet<HealthResponse>("/api/v1/health", signal);
  return { health, latencyMs: Math.round(performance.now() - start) };
}
