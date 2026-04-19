/**
 * Auto-scheduling of 4 daily reminder notifications for Lo Sapevi che?
 */
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import { Platform } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";

const SCHEDULED_KEY = "@losapevi_notifs_scheduled_v2";

// 4 daily slots with varied messages
const DAILY_SLOTS = [
  { hour: 8, minute: 0, title: "Lo Sapevi che?", body: "Inizia la giornata con una curiosità ☀️" },
  { hour: 13, minute: 0, title: "Pausa mentale", body: "Una curiosità per la pausa pranzo 🍽️✨" },
  { hour: 17, minute: 0, title: "Lo Sapevi che?", body: "Scopri qualcosa di nuovo prima di cena 🌅" },
  { hour: 21, minute: 0, title: "Buonanotte curioso", body: "Una perla di sapere prima di dormire 🌙" },
];

export async function ensureDailyNotifications(force = false): Promise<"granted" | "denied" | "simulator" | "error"> {
  try {
    if (!Device.isDevice) return "simulator";

    const already = await AsyncStorage.getItem(SCHEDULED_KEY);
    if (already === "true" && !force) return "granted";

    if (Platform.OS === "android") {
      await Notifications.setNotificationChannelAsync("default", {
        name: "Curiosità quotidiane",
        importance: Notifications.AndroidImportance.HIGH,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: "#D4AF37",
      });
    }

    const { status: existing } = await Notifications.getPermissionsAsync();
    let finalStatus = existing;
    if (existing !== "granted") {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== "granted") return "denied";

    // Cancel any previously scheduled reminders to avoid duplicates
    await Notifications.cancelAllScheduledNotificationsAsync();

    // Schedule the 4 daily slots
    for (const slot of DAILY_SLOTS) {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: slot.title,
          body: slot.body,
          sound: "default",
        },
        trigger: {
          type: Notifications.SchedulableTriggerInputTypes.DAILY,
          hour: slot.hour,
          minute: slot.minute,
        } as any,
      });
    }

    await AsyncStorage.setItem(SCHEDULED_KEY, "true");
    return "granted";
  } catch (e) {
    console.warn("ensureDailyNotifications error", e);
    return "error";
  }
}

export async function disableDailyNotifications() {
  try {
    await Notifications.cancelAllScheduledNotificationsAsync();
    await AsyncStorage.removeItem(SCHEDULED_KEY);
  } catch {}
}

export async function areNotificationsActive(): Promise<boolean> {
  try {
    const v = await AsyncStorage.getItem(SCHEDULED_KEY);
    if (v !== "true") return false;
    const { status } = await Notifications.getPermissionsAsync();
    return status === "granted";
  } catch {
    return false;
  }
}

export const NOTIFICATION_SLOTS = DAILY_SLOTS.map((s) => `${s.hour.toString().padStart(2, "0")}:${s.minute.toString().padStart(2, "0")}`);
