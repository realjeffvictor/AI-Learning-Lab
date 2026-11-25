export type Role = "student" | "instructor" | "admin";
export type ExperienceLevel = "beginner" | "intermediate" | "advanced";

export interface UserProfile {
  display_name: string;
  bio: string | null;
  experience_level: ExperienceLevel;
}

export interface User {
  id: string;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
  profile: UserProfile;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: User;
}

export interface UserPage {
  items: User[];
  page: number;
  page_size: number;
  total: number;
}
