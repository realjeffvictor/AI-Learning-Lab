import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";

import { Button } from "../components/Button";
import { SignInLayout } from "../features/auth/SignInLayout";
import { useAuth } from "../features/auth/AuthContext";
import { describeError } from "../lib/api/messages";

export function LoginPage() {
  const { status, login } = useAuth();
  const location = useLocation();
  const requested = (location.state as { from?: string } | null)?.from;
  const destination = requested && requested.startsWith("/") ? requested : "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  if (status === "authenticated") return <Navigate to={destination} replace />;

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
    } catch (caught) {
      setError(describeError(caught));
    } finally {
      setBusy(false);
    }
  }

  return (
    <SignInLayout
      title="Sign in"
      subtitle="Continue where you left off."
      footer={
        <>
          New here?{" "}
          <Link to="/register" className="text-signal underline underline-offset-4">
            Create an account
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-5" noValidate>
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
            className="h-11 rounded-lg border border-[#CBD5E1] bg-white px-3 text-sm text-[#0F172A] placeholder:text-[#94A3B8]"
          />
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="password" className="text-[11px] font-semibold tracking-[0.04em] text-[#475569]">PASSWORD</label>
          <div className="relative">
            <input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="h-11 w-full rounded-lg border border-[#CBD5E1] bg-white px-3 pr-12 text-sm text-[#0F172A] placeholder:text-[#94A3B8]"
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
          <div className="-mt-0.5 flex justify-end">
            <button
              type="button"
              disabled
              title="Password recovery is not available yet."
              className="text-xs text-[#64748B] underline underline-offset-2 disabled:cursor-not-allowed"
            >
              Forgot password?
            </button>
          </div>
        </div>
        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}
        <Button
          type="submit"
          disabled={busy || !email || !password}
          className="h-11 rounded-lg !bg-[#D95D39] text-sm font-semibold !text-white hover:!bg-[#c84f2f] disabled:!opacity-100"
        >
          {busy ? "Signing in..." : "Sign in"}
        </Button>
      </form>
    </SignInLayout>
  );
}
