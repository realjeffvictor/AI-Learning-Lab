import { apiGet } from "../../lib/api/client";
import { authedRequest } from "../auth/session";

export interface CertRequirement {
  key: string;
  label: string;
  done: number;
  total: number;
}
export interface IssuedCertificate {
  code: string;
  course_slug: string;
  course_title: string;
  holder_name: string;
  issued_at: string;
}
export interface CertificateStatus {
  course_slug: string;
  course_title: string;
  eligible: boolean;
  message: string | null;
  requirements: CertRequirement[];
  certificate: IssuedCertificate | null;
}
export interface PublicCertificate {
  valid: boolean;
  holder_name: string;
  course_title: string;
  issued_at: string;
}

export const fetchCertificates = (signal?: AbortSignal) =>
  authedRequest<CertificateStatus[]>("/api/v1/certificates", { signal });

export const issueCertificate = (courseSlug: string) =>
  authedRequest<IssuedCertificate>(`/api/v1/certificates/${encodeURIComponent(courseSlug)}`, { method: "POST" });

/** Public: no sign-in needed. */
export const verifyCertificate = (code: string, signal?: AbortSignal) =>
  apiGet<PublicCertificate>(`/api/v1/certificates/verify/${encodeURIComponent(code)}`, signal);
