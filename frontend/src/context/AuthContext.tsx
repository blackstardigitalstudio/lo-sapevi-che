import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api, ApiError } from "../lib/api";

type User = {
  id: string;
  email: string;
  name: string;
  interests: string[];
  interest_weights: Record<string, number>;
  sub_interests?: Record<string, string[]>;
  stats: { liked: number; disliked: number; bookmarked: number; seen: number };
  streak_days?: number;
  best_streak?: number;
  trophies?: string[];
  ai_generated_count?: number;
  has_security_question?: boolean;
  created_at: string;
};

type AuthState = {
  user: User | null | undefined; // undefined = loading, null = logged out
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    name: string,
    interests: string[],
    security_question: string,
    security_answer: string,
  ) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null | undefined>(undefined);

  /**
   * Robust refresh:
   *  - If there's no token saved → user is logged out.
   *  - If there IS a token:
   *    1. Load the cached user immediately so the UI doesn't bounce to login.
   *    2. Try to fetch fresh /auth/me in the background.
   *       - 200 → update state + cache.
   *       - 401 → token is invalid, force logout.
   *       - Other errors (network offline, 5xx, timeout) → keep the cached user.
   */
  const refresh = async () => {
    const token = await api.getToken();
    if (!token) {
      await api.setCachedUser(null);
      setUser(null);
      return;
    }

    // Hydrate from cache first (instant, no network) so users never see the
    // login screen after a cold-start when a valid session already exists.
    const cached = await api.getCachedUser();
    if (cached) setUser(cached);

    try {
      const me = await api.me();
      setUser(me);
      await api.setCachedUser(me);
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 401) {
        // Real auth failure: token no longer valid on the server.
        await api.setToken(null);
        await api.setCachedUser(null);
        setUser(null);
        return;
      }
      // Network / server blip: keep the cached user if we have one, otherwise
      // mark as logged-out so the login screen appears.
      if (!cached) setUser(null);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.login({ email, password });
    await api.setToken(res.token);
    await api.setCachedUser(res.user);
    setUser(res.user);
  };

  const register = async (
    email: string,
    password: string,
    name: string,
    interests: string[],
    security_question: string,
    security_answer: string,
  ) => {
    const res = await api.register({
      email,
      password,
      name,
      interests,
      security_question,
      security_answer,
    });
    await api.setToken(res.token);
    await api.setCachedUser(res.user);
    setUser(res.user);
  };

  const logout = async () => {
    await api.setToken(null);
    await api.setCachedUser(null);
    setUser(null);
  };

  return <Ctx.Provider value={{ user, login, register, logout, refresh }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const c = useContext(Ctx);
  if (!c) throw new Error("useAuth must be used inside AuthProvider");
  return c;
}
