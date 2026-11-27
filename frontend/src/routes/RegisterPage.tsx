import { useState, type FormEvent } from "react";
import { Link, Navigate } from "react-router-dom";

import { Button } from "../components/Button";
import { AuthLayout } from "../features/auth/AuthLayout";
import { useAuth } from "../features/auth/AuthContext";
import { describeError } from "../lib/api/messages";

export function RegisterPage() {
  const { status, register } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  if (status === "authenticated") return <Navigate to="/dashboard" replace />;

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await register(email, password, displayName);
    } catch (caught) {
      setError(describeError(caught));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Free to start. Everything you do is saved to your profile."
      footer={
        <>
          Already registered?{" "}
          <Link to="/login" className="text-signal underline underline-offset-4">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-5" noValidate>
        <div className="flex flex-col gap-2">
          <label htmlFor="display_name" className="text-[11px] font-semibold tracking-[0.04em] text-[#475569]">DISPLAY NAME</label>
          <input
            id="display_name"
            name="display_name"
            autoComplete="name"
            maxLength={80}
            required
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
            className="h-11 rounded-lg border border-[#CBD5E1] bg-white px-3 text-sm text-[#0F172A]"
          />
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="email" className="text-[11px] font-semibold tracking-[0.04em] text-[#475569]">EMAIL</label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="h-11 rounded-lg border border-[#CBD5E1] bg-white px-3 text-sm text-[#0F172A]"
          />
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="password" className="text-[11px] font-semibold tracking-[0.04em] text-[#475569]">PASSWORD</label>
          <div className="relative">
            <input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              minLength={10}
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="h-11 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 pr-12 text-sm text-[#0F172A]"
              aria-describedby="password-hint"
            />
            <button
              type="button"
              aria-label={showPassword ? "Hide password" : "Show password"}
              aria-pressed={showPassword}
              onClick={() => setShowPassword((visible) => !visible)}
              className="absolute inset-y-0 right-0 flex w-11 items-center justify-center text-[#64748B] hover:text-[#0F172A]"
            >
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6Z" />
                <circle cx="12" cy="12" r="2.5" />
                {showPassword && <path d="m4 4 16 16" />}
              </svg>
            </button>
          </div>
          <p id="password-hint" className="text-xs text-[#64748B]">At least 10 characters. A passphrase works well.</p>
        </div>
        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}
        <Button
          type="submit"
          disabled={busy || !displayName || !email || password.length < 10}
          className="h-11 rounded-lg !bg-[#D95D39] text-sm font-semibold !text-white hover:!bg-[#c84f2f] disabled:!opacity-100"
        >
          {busy ? "Creating account..." : "Create account"}
        </Button>
      </form>
    </AuthLayout>
  );
}
