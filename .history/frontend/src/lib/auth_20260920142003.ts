export type AuthUser = {
  username: string;
  name: string;
  token: string;
};

const AUTH_STORAGE_KEY = "pm_auth_user";

export const getStoredUser = (): AuthUser | null => {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
};

export const setStoredUser = (user: AuthUser): void => {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
  } catch {
    // Ignore storage quota or disabled errors
  }
};

export const clearStoredUser = (): void => {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(AUTH_STORAGE_KEY);
  } catch {
    // Ignore storage errors
  }
};

export const loginWithCredentials = async (
  username: string,
  password: string
): Promise<AuthUser> => {
  // First try backend API if available
  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      const user: AuthUser = {
        username: data.username,
        name: data.name,
        token: data.token,
      };
      setStoredUser(user);
      return user;
    }

    if (response.status === 401) {
      throw new Error("Invalid username or password");
    }
  } catch (err: unknown) {
    if (err instanceof Error && err.message === "Invalid username or password") {
      throw err;
    }
    // Network or static mode fallback: hardcoded credentials check
  }

  // Hardcoded MVP fallback
  if (username === "user" && password === "password") {
    const user: AuthUser = {
      username: "user",
      name: "Demo User",
      token: "token-user-pm-session",
    };
    setStoredUser(user);
    return user;
  }

  throw new Error("Invalid username or password");
};
