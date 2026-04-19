import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api } from "../lib/api";

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
  created_at: string;
};

type AuthState = {
  user: User | null | undefined; // undefined = loading, null = logged out
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string, interests: string[]) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null | undefined>(undefined);

  const refresh = async () => {
    try {
      const token = await api.getToken();
      if (!token) {
        setUser(null);
        return;
      }
      const me = await api.me();
      setUser(me);
    } catch {
      await api.setToken(null);
      setUser(null);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.login({ email, password });
    await api.setToken(res.token);
    setUser(res.user);
  };

  const register = async (email: string, password: string, name: string, interests: string[]) => {
    const res = await api.register({ email, password, name, interests });
    await api.setToken(res.token);
    setUser(res.user);
  };

  const logout = async () => {
    await api.setToken(null);
    setUser(null);
  };

  return <Ctx.Provider value={{ user, login, register, logout, refresh }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const c = useContext(Ctx);
  if (!c) throw new Error("useAuth must be used inside AuthProvider");
  return c;
}
