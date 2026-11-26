import type { CertRequirement } from "./api";

/** The requirements that are not yet met, in their original order. */
export function unmet(requirements: readonly CertRequirement[]): CertRequirement[] {
  return requirements.filter((item) => item.done < item.total);
}

export function verifyPath(code: string): string {
  return `/verify/${encodeURIComponent(code)}`;
}
