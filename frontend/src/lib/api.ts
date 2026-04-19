import AsyncStorage from "@react-native-async-storage/async-storage";

const API_BASE = `${process.env.EXPO_PUBLIC_BACKEND_URL}/api`;
const TOKEN_KEY = "@losapevi_token";

async function authHeaders() {
  const token = await AsyncStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path: string, opts: RequestInit = {}) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(await authHeaders()),
    ...((opts.headers as Record<string, string>) || {}),
  };
  const res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
  const text = await res.text();
  let data: any = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text };
  }
  if (!res.ok) {
    const detail = data?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
        ? detail.map((d: any) => d?.msg || JSON.stringify(d)).join(", ")
        : "Errore di rete";
    throw new Error(message);
  }
  return data;
}

export const api = {
  setToken: async (t: string | null) => {
    if (t) await AsyncStorage.setItem(TOKEN_KEY, t);
    else await AsyncStorage.removeItem(TOKEN_KEY);
  },
  getToken: async () => AsyncStorage.getItem(TOKEN_KEY),
  register: (payload: { email: string; password: string; name: string; interests: string[] }) =>
    request("/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload: { email: string; password: string }) =>
    request("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  me: () => request("/auth/me"),
  updateInterests: (interests: string[]) =>
    request("/auth/interests", { method: "POST", body: JSON.stringify({ interests }) }),
  setPushToken: (token: string) =>
    request("/auth/push-token", { method: "POST", body: JSON.stringify({ token }) }),
  categories: () => request("/categories"),
  subcategories: (category: string) => request(`/subcategories/${encodeURIComponent(category)}`),
  updateSubInterests: (sub_interests: Record<string, string[]>) =>
    request("/auth/sub-interests", { method: "POST", body: JSON.stringify({ sub_interests }) }),
  feed: (limit = 20) => request(`/feed?limit=${limit}`),
  markSeen: (factId: string) => request(`/facts/${factId}/seen`, { method: "POST" }),
  react: (factId: string, action: "like" | "dislike") =>
    request(`/facts/${factId}/react`, { method: "POST", body: JSON.stringify({ action }) }),
  bookmark: (factId: string) => request(`/facts/${factId}/bookmark`, { method: "POST" }),
  bookmarks: () => request("/facts/bookmarks"),
  liked: () => request("/facts/liked"),
  fact: (factId: string) => request(`/facts/${factId}`),
  generate: (category?: string) =>
    request(`/facts/generate`, { method: "POST", body: JSON.stringify({ category: category || null }) }),
  sendTestPush: () => request(`/notifications/send-test`, { method: "POST" }),
  checkin: () => request(`/auth/checkin`, { method: "POST" }),
  preview: () => request(`/preview`),
  trophies: () => request(`/trophies`),
  bulkGenerate: (count: number, category?: string) =>
    request(`/facts/bulk-generate`, {
      method: "POST",
      body: JSON.stringify({ count, category: category || null }),
    }),
};

export const theme = {
  bg: "#05060A",
  surface: "#12141D",
  surfaceAlt: "#1A1D28",
  primary: "#D4AF37",
  primaryDark: "#B5952F",
  text: "#FFFFFF",
  textMuted: "#A0AAB2",
  border: "#2A2D35",
  error: "#E63946",
  success: "#2A9D8F",
};
