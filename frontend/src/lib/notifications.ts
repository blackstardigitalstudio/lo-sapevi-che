/**
 * Daily random notifications for Lo Sapevi che?
 * User picks a time window; we schedule 4 notifications per day at random
 * moments within that window, each with a REAL fact title+body and deep-link.
 */
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import { Platform } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { api } from "./api";
import i18n from "./i18n";

const STATE_KEY = "@losapevi_notifs_state_v3";

export type WindowKey = "mattina" | "pomeriggio" | "sera" | "sorpresa";

export const WINDOWS: Record<WindowKey, { labelKey: string; icon: string; startHour: number; endHour: number }> = {
  mattina: { labelKey: "notif.window.mattina", icon: "sunny", startHour: 7, endHour: 10 },
  pomeriggio: { labelKey: "notif.window.pomeriggio", icon: "partly-sunny", startHour: 12, endHour: 16 },
  sera: { labelKey: "notif.window.sera", icon: "moon", startHour: 18, endHour: 22 },
  sorpresa: { labelKey: "notif.window.sorpresa", icon: "dice", startHour: 8, endHour: 22 },
};

export const NOTIF_PER_DAY = 4;
export const SCHEDULE_DAYS = 25; // ~100 programmate su 25 giorni × 4/giorno

function getTitles(): string[] {
  return i18n.t("notif.titles", { returnObjects: true }) as string[];
}
function getBodies(): string[] {
  return i18n.t("notif.bodies", { returnObjects: true }) as string[];
}
function getDidYouKnow(): string {
  return i18n.t("feed.didYouKnow");
}

function pick<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

type NotifState = {
  enabled: boolean;
  window: WindowKey;
  scheduledCount: number;
  nextAt?: string; // ISO string
};

export async function getNotifState(): Promise<NotifState> {
  try {
    const raw = await AsyncStorage.getItem(STATE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return { enabled: false, window: "sorpresa", scheduledCount: 0 };
}

async function saveNotifState(s: NotifState) {
  try {
    await AsyncStorage.setItem(STATE_KEY, JSON.stringify(s));
  } catch {}
}

async function ensurePermission(): Promise<"granted" | "denied" | "simulator"> {
  if (!Device.isDevice) return "simulator";
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "Curiosità quotidiane",
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#D4AF37",
    });
  }
  const { status: existing } = await Notifications.getPermissionsAsync();
  if (existing === "granted") return "granted";
  const { status } = await Notifications.requestPermissionsAsync();
  return status === "granted" ? "granted" : "denied";
}

function randomTimesInWindow(startHour: number, endHour: number, count: number): Array<{ h: number; m: number }> {
  // Generate `count` random times between startHour:00 and endHour:59 (inclusive window)
  const minutesStart = startHour * 60;
  const minutesEnd = endHour * 60 + 59;
  const step = Math.floor((minutesEnd - minutesStart) / count);
  const out: Array<{ h: number; m: number }> = [];
  for (let i = 0; i < count; i++) {
    const base = minutesStart + step * i;
    const jitter = Math.floor(Math.random() * Math.max(step - 10, 10));
    const total = Math.min(base + jitter, minutesEnd);
    out.push({ h: Math.floor(total / 60), m: total % 60 });
  }
  return out;
}

export async function scheduleNotifications(windowKey: WindowKey): Promise<{
  ok: boolean;
  reason?: "simulator" | "denied" | "error";
  state?: NotifState;
}> {
  try {
    const perm = await ensurePermission();
    if (perm === "simulator") return { ok: false, reason: "simulator" };
    if (perm === "denied") return { ok: false, reason: "denied" };

    await Notifications.cancelAllScheduledNotificationsAsync();

    // Fetch real facts from the user's personalized feed to use as content.
    // We ask for a big batch; if fewer facts, we cycle.
    let factPool: Array<{ id: string; title: string; short_fact: string }> = [];
    try {
      const res = await api.feed(100);
      factPool = (res?.facts || []).map((f: any) => ({
        id: f.id,
        title: f.title,
        short_fact: f.short_fact,
      }));
    } catch {}

    const win = WINDOWS[windowKey];
    const now = new Date();
    let nextAt: Date | null = null;
    let scheduled = 0;

    for (let d = 0; d < SCHEDULE_DAYS; d++) {
      const times = randomTimesInWindow(win.startHour, win.endHour, NOTIF_PER_DAY);
      for (const t of times) {
        const date = new Date(now);
        date.setDate(now.getDate() + d);
        date.setHours(t.h, t.m, 0, 0);
        if (date.getTime() <= now.getTime() + 30_000) continue; // skip past

        // Pick a fact from pool (cycle). Fall back to generic if pool empty.
        const fact = factPool.length > 0 ? factPool[scheduled % factPool.length] : null;
        const title = fact ? getDidYouKnow() : pick(getTitles());
        const body = fact ? fact.title : pick(getBodies());
        const data: any = fact ? { fact_id: fact.id } : {};

        try {
          await Notifications.scheduleNotificationAsync({
            content: {
              title,
              body,
              data,
              sound: "default",
            },
            trigger: {
              type: Notifications.SchedulableTriggerInputTypes.DATE,
              date,
            } as any,
          });
          scheduled++;
          if (!nextAt || date < nextAt) nextAt = date;
        } catch {}
      }
    }

    const state: NotifState = {
      enabled: true,
      window: windowKey,
      scheduledCount: scheduled,
      nextAt: nextAt ? nextAt.toISOString() : undefined,
    };
    await saveNotifState(state);
    return { ok: true, state };
  } catch (e) {
    return { ok: false, reason: "error" };
  }
}

export async function disableNotifications(): Promise<void> {
  try {
    await Notifications.cancelAllScheduledNotificationsAsync();
    const cur = await getNotifState();
    await saveNotifState({ ...cur, enabled: false, scheduledCount: 0, nextAt: undefined });
  } catch {}
}

/**
 * Called on app open: if user has never configured notifications,
 * auto-enable with default "Sorpresa" window and schedule.
 */
export async function ensureDefaultScheduling(): Promise<NotifState | null> {
  try {
    const s = await getNotifState();
    if (s.enabled && s.scheduledCount > 0) {
      // Already configured; check permission still granted
      if (!Device.isDevice) return s;
      const { status } = await Notifications.getPermissionsAsync();
      if (status !== "granted") return s;
      return s;
    }
    // Auto-schedule with Sorpresa window (default)
    const res = await scheduleNotifications("sorpresa");
    return res.state || null;
  } catch {
    return null;
  }
}
