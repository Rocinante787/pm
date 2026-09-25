"use client";

import { useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";
import { clearStoredUser, getStoredUser, type AuthUser } from "@/lib/auth";

export default function Home() {
  const [authUser, setAuthUser] = useState<AuthUser | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const user = getStoredUser();
    setAuthUser(user);
    setIsInitialized(true);
  }, []);

  const handleLogout = () => {
    clearStoredUser();
    setAuthUser(null);
  };

  if (!isInitialized) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--surface)]">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--primary-blue)] border-t-transparent" />
      </div>
    );
  }

  if (!authUser) {
    return <LoginForm onSuccess={(user) => setAuthUser(user)} />;
  }

  return <KanbanBoard user={authUser} onLogout={handleLogout} />;
}
