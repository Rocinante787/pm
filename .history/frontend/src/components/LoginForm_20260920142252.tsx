"use client";

import { useState, type FormEvent } from "react";
import { loginWithCredentials, type AuthUser } from "@/lib/auth";

type LoginFormProps = {
  onSuccess: (user: AuthUser) => void;
};

export const LoginForm = ({ onSuccess }: LoginFormProps) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const user = await loginWithCredentials(username.trim(), password);
      onSuccess(user);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred during sign in.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      {/* Background gradients */}
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <div className="relative w-full max-w-md rounded-[32px] border border-[var(--stroke)] bg-white/90 p-8 shadow-[var(--shadow)] backdrop-blur sm:p-10">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-[var(--stroke)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
            <span className="h-2 w-2 rounded-full bg-[var(--accent-yellow)]" />
            Project Management MVP
          </div>
          <h1 className="mt-4 font-display text-3xl font-bold text-[var(--navy-dark)]">
            Sign In
          </h1>
          <p className="mt-2 text-sm text-[var(--gray-text)]">
            Use username <span className="font-semibold text-[var(--navy-dark)]">user</span> and password <span className="font-semibold text-[var(--navy-dark)]">password</span> to enter.
          </p>
        </div>

        {error && (
          <div
            role="alert"
            className="mb-6 rounded-2xl border border-red-200 bg-red-50/80 px-4 py-3 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="username"
              className="block text-xs font-semibold uppercase tracking-wider text-[var(--gray-text)]"
            >
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              placeholder="user"
              className="mt-2 w-full rounded-xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm font-medium text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)] focus:bg-white"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-xs font-semibold uppercase tracking-wider text-[var(--gray-text)]"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              placeholder="password"
              className="mt-2 w-full rounded-xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm font-medium text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)] focus:bg-white"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-full bg-[var(--secondary-purple)] py-3 text-sm font-semibold uppercase tracking-wide text-white transition hover:brightness-110 disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
};

