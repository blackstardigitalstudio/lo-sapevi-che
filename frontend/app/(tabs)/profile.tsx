import { useCallback, useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Platform,
  Share,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import * as Notifications from "expo-notifications";
import { useFocusEffect, useRouter } from "expo-router";
import { api, theme } from "../../src/lib/api";
import { useAuth } from "../../src/context/AuthContext";
import { LanguagePicker } from "../../src/components/LanguagePicker";
import { useTranslation } from "react-i18next";
import {
  scheduleNotifications,
  disableNotifications,
  getNotifState,
  WINDOWS,
  WindowKey,
  NOTIF_PER_DAY,
  SCHEDULE_DAYS,
} from "../../src/lib/notifications";

export default function Profile() {
  const router = useRouter();
  const { user, logout, refresh } = useAuth();
  const { t, i18n } = useTranslation();
  const [notifEnabled, setNotifEnabled] = useState<boolean>(true);
  const [notifWindow, setNotifWindow] = useState<WindowKey>("sorpresa");
  const [nextAt, setNextAt] = useState<string | undefined>(undefined);
  const [scheduledCount, setScheduledCount] = useState<number>(0);
  const [busy, setBusy] = useState(false);
  const [trophies, setTrophies] = useState<any[]>([]);

  const loadNotifState = async () => {
    const s = await getNotifState();
    setNotifEnabled(s.enabled);
    setNotifWindow(s.window);
    setNextAt(s.nextAt);
    setScheduledCount(s.scheduledCount);
  };

  useFocusEffect(
    useCallback(() => {
      refresh();
      api.trophies(i18n.language).then(setTrophies).catch(() => {});
      loadNotifState();
    }, [i18n.language])
  );

  const shareProfile = async () => {
    if (!user) return;
    try {
      const earned = trophies.filter((t) => t.earned).length;
      await Share.share({
        message: t("profile.shareProfileMsg", {
          seen: user.stats.seen,
          liked: user.stats.liked,
          streak: user.streak_days || 0,
          trophies: earned,
        }),
      });
    } catch {}
  };

  if (!user) {
    return (
      <View style={styles.loader}>
        <ActivityIndicator color={theme.primary} />
      </View>
    );
  }

  const topCategories = Object.entries(user.interest_weights || {})
    .sort(([, a], [, b]) => (b as number) - (a as number))
    .slice(0, 5);

  const onToggle = async () => {
    setBusy(true);
    try {
      if (notifEnabled) {
        await disableNotifications();
        setNotifEnabled(false);
        setScheduledCount(0);
        setNextAt(undefined);
      } else {
        const res = await scheduleNotifications(notifWindow);
        if (res.ok && res.state) {
          setNotifEnabled(true);
          setScheduledCount(res.state.scheduledCount);
          setNextAt(res.state.nextAt);
        } else if (res.reason === "denied") {
          Alert.alert(t("profile.permissionDeniedTitle"), t("profile.permissionDeniedBody"));
        } else if (res.reason === "simulator") {
          Alert.alert(t("profile.simulatorTitle"), t("profile.simulatorBody"));
        }
      }
    } finally {
      setBusy(false);
    }
  };

  const pickWindow = async (key: WindowKey) => {
    setBusy(true);
    try {
      const res = await scheduleNotifications(key);
      if (res.ok && res.state) {
        setNotifEnabled(true);
        setNotifWindow(key);
        setScheduledCount(res.state.scheduledCount);
        setNextAt(res.state.nextAt);
      }
    } finally {
      setBusy(false);
    }
  };

  const testPush = async () => {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: t("profile.notifTitle"),
          body: t("profile.testNotifBody"),
          sound: "default",
        },
        trigger: { type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL, seconds: 3 } as any,
      });
      Alert.alert(t("profile.testPushSentTitle"), t("profile.testPushSentBody"));
    } catch (e: any) {
      Alert.alert(t("common.error"), e?.message || t("profile.sendError"));
    }
  };

  const formatNextAt = (iso?: string) => {
    if (!iso) return "—";
    try {
      const d = new Date(iso);
      const date = d.toLocaleDateString("it-IT");
      const time = d.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
      return `${date}, ${time}`;
    } catch {
      return iso;
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={["top"]} testID="profile-screen">
      <ScrollView contentContainerStyle={styles.scroll}>
        <View style={styles.header}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {(user.name || "?").charAt(0).toUpperCase()}
            </Text>
          </View>
          <Text style={styles.name}>{user.name}</Text>
          <Text style={styles.email}>{user.email}</Text>
        </View>

        <View style={styles.statsRow}>
          <Stat label={t("profile.readFacts")} value={user.stats.seen} />
          <Stat label={t("profile.liked")} value={user.stats.liked} />
          <Stat label={t("profile.bookmarked")} value={user.stats.bookmarked} />
        </View>

        <View style={styles.streakCard} testID="streak-card">
          <View style={styles.streakLeft}>
            <Text style={styles.streakEmoji}>🔥</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.streakValue}>
              {user.streak_days || 0} <Text style={styles.streakUnit}>{t("profile.days")}</Text>
            </Text>
            <Text style={styles.streakLabel}>{t("profile.currentStreak")}</Text>
            {user.best_streak ? (
              <Text style={styles.streakBest}>{t("profile.bestRecord", { days: user.best_streak })}</Text>
            ) : null}
          </View>
          <TouchableOpacity style={styles.shareMini} onPress={shareProfile} testID="share-profile">
            <Ionicons name="share-social-outline" size={20} color={theme.primary} />
          </TouchableOpacity>
        </View>

        <Text style={styles.sectionTitle}>{t("profile.trophies")} · {trophies.filter((t) => t.earned).length}/{trophies.length}</Text>
        <View style={styles.trophyGrid}>
          {trophies.map((t) => (
            <View
              key={t.id}
              testID={`trophy-${t.id}`}
              style={[styles.trophyItem, !t.earned && styles.trophyItemLocked]}
            >
              <View style={[styles.trophyIcon, !t.earned && styles.trophyIconLocked]}>
                <Ionicons
                  name={t.icon as any}
                  size={20}
                  color={t.earned ? theme.bg : theme.textMuted}
                />
              </View>
              <Text
                style={[styles.trophyName, !t.earned && styles.trophyNameLocked]}
                numberOfLines={1}
              >
                {t.name}
              </Text>
            </View>
          ))}
        </View>

        <Text style={styles.sectionTitle}>{t("profile.topInterests")}</Text>
        <View style={styles.weightsBox}>
          {topCategories.map(([cat, w]) => {
            const pct = Math.min(100, Math.round(((w as number) / 3) * 100));
            return (
              <View key={cat} style={styles.weightRow}>
                <View style={styles.weightHead}>
                  <Text style={styles.weightCat}>{cat}</Text>
                  <Text style={styles.weightPct}>{pct}%</Text>
                </View>
                <View style={styles.barBg}>
                  <View style={[styles.barFill, { width: `${pct}%` }]} />
                </View>
              </View>
            );
          })}
        </View>

        <View style={styles.notifHeaderRow}>
          <Text style={styles.sectionTitle}>{t("profile.dailyNotifications")}</Text>
          <TouchableOpacity
            testID="notif-toggle"
            onPress={onToggle}
            disabled={busy}
            style={[styles.toggle, notifEnabled && styles.toggleOn]}
          >
            <View style={[styles.toggleKnob, notifEnabled && styles.toggleKnobOn]} />
          </TouchableOpacity>
        </View>
        <Text style={styles.notifSubtitle}>
          {t("profile.notifSummary", { n: NOTIF_PER_DAY, count: scheduledCount })}
        </Text>

        <Text style={styles.microLabel}>{t("profile.timeWindow")}</Text>
        <View style={styles.windowsGrid}>
          {(Object.keys(WINDOWS) as WindowKey[]).map((k) => {
            const w = WINDOWS[k];
            const active = notifWindow === k && notifEnabled;
            return (
              <TouchableOpacity
                key={k}
                testID={`window-${k}`}
                style={[styles.windowBtn, active && styles.windowBtnOn]}
                onPress={() => pickWindow(k)}
                disabled={busy}
                activeOpacity={0.85}
              >
                <Ionicons name={w.icon as any} size={18} color={active ? theme.bg : theme.text} />
                <Text style={[styles.windowText, active && styles.windowTextOn]}>{t(w.labelKey)}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {notifEnabled && (
          <View style={styles.nextAtRow}>
            <Ionicons name="notifications" size={14} color={theme.primary} />
            <Text style={styles.nextAtText}>{t("profile.nextNotif", { when: formatNextAt(nextAt) })}</Text>
          </View>
        )}

        <TouchableOpacity style={styles.ghostBtn} onPress={testPush} testID="test-push">
          <Ionicons name="notifications-outline" size={16} color={theme.primary} />
          <Text style={styles.ghostBtnText}>{t("profile.testPush")}</Text>
        </TouchableOpacity>

        <Text style={styles.sectionTitle}>{t("profile.account")}</Text>
        <TouchableOpacity
          style={styles.rowBtn}
          onPress={() => router.push("/onboarding")}
          testID="edit-interests"
        >
          <Ionicons name="options-outline" size={20} color={theme.text} />
          <Text style={styles.rowText}>{t("profile.editInterests")}</Text>
          <Ionicons name="chevron-forward" size={18} color={theme.textMuted} />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.rowBtn}
          onPress={() => router.push("/security")}
          testID="security-settings"
        >
          <Ionicons name="shield-checkmark-outline" size={20} color={theme.text} />
          <Text style={styles.rowText}>
            {user.has_security_question ? t("profile.securityQuestion") : t("profile.setSecurityQuestion")}
          </Text>
          {!user.has_security_question && (
            <View style={styles.badge}>
              <Text style={styles.badgeText}>!</Text>
            </View>
          )}
          <Ionicons name="chevron-forward" size={18} color={theme.textMuted} />
        </TouchableOpacity>

        <LanguagePicker variant="row" onChange={() => {}} />

        <TouchableOpacity
          style={[styles.rowBtn, { borderColor: theme.error }]}
          onPress={() => {
            Alert.alert(t("profile.logoutConfirmTitle"), t("profile.logoutConfirmBody"), [
              { text: t("common.cancel"), style: "cancel" },
              {
                text: t("profile.logout"),
                style: "destructive",
                onPress: async () => {
                  await logout();
                  router.replace("/auth/login");
                },
              },
            ]);
          }}
          testID="logout-btn"
        >
          <Ionicons name="log-out-outline" size={20} color={theme.error} />
          <Text style={[styles.rowText, { color: theme.error }]}>{t("profile.logout")}</Text>
          <View style={{ width: 18 }} />
        </TouchableOpacity>

        <Text style={styles.version}>{t("profile.appVersion")}</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <View style={styles.stat}>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.bg },
  loader: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: theme.bg },
  scroll: { padding: 24, paddingBottom: 80 },
  header: { alignItems: "center", marginBottom: 24 },
  avatar: {
    width: 84,
    height: 84,
    borderRadius: 42,
    backgroundColor: theme.primary,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 14,
  },
  avatarText: { color: theme.bg, fontSize: 34, fontWeight: "700" },
  name: { color: theme.text, fontSize: 26, fontWeight: "300", fontStyle: "italic" },
  email: { color: theme.textMuted, fontSize: 13, marginTop: 4 },
  statsRow: {
    flexDirection: "row",
    backgroundColor: theme.surface,
    borderRadius: 18,
    padding: 16,
    justifyContent: "space-around",
    marginBottom: 16,
    borderWidth: 1,
    borderColor: theme.border,
  },
  stat: { alignItems: "center" },
  statValue: { color: theme.primary, fontSize: 26, fontWeight: "700" },
  statLabel: { color: theme.textMuted, fontSize: 12, letterSpacing: 0.5, marginTop: 2 },
  sectionTitle: {
    color: theme.textMuted,
    textTransform: "uppercase",
    fontSize: 11,
    letterSpacing: 1.5,
    marginTop: 16,
    marginBottom: 10,
  },
  weightsBox: { backgroundColor: theme.surface, borderRadius: 18, padding: 16, borderWidth: 1, borderColor: theme.border },
  weightRow: { marginBottom: 12 },
  weightHead: { flexDirection: "row", justifyContent: "space-between", marginBottom: 6 },
  weightCat: { color: theme.text, fontSize: 14, fontWeight: "500" },
  weightPct: { color: theme.primary, fontSize: 12, fontWeight: "600" },
  barBg: { height: 6, backgroundColor: theme.border, borderRadius: 3, overflow: "hidden" },
  barFill: { height: "100%", backgroundColor: theme.primary },
  actionCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: theme.surface,
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: theme.border,
    gap: 12,
  },
  actionTitle: { color: theme.text, fontSize: 15, fontWeight: "500" },
  actionSubtitle: { color: theme.textMuted, fontSize: 12, marginTop: 4 },
  actionBtn: { backgroundColor: theme.primary, paddingHorizontal: 18, paddingVertical: 10, borderRadius: 999 },
  actionBtnText: { color: theme.bg, fontWeight: "700", fontSize: 13 },
  ghostBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    paddingVertical: 12,
    marginTop: 10,
    borderWidth: 1,
    borderColor: theme.border,
    borderRadius: 14,
  },
  ghostText: { color: theme.primary, fontWeight: "600" },
  rowBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    backgroundColor: theme.surface,
    borderRadius: 14,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: theme.border,
  },
  rowText: { color: theme.text, fontSize: 15, flex: 1 },
  badge: {
    backgroundColor: theme.primary,
    width: 20,
    height: 20,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 8,
  },
  badgeText: { color: theme.bg, fontWeight: "700", fontSize: 13 },
  version: { color: theme.textMuted, fontSize: 11, textAlign: "center", marginTop: 30 },
  streakCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: theme.surface,
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: theme.primary,
    marginBottom: 8,
    gap: 16,
  },
  streakLeft: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "rgba(212,175,55,0.15)",
    alignItems: "center",
    justifyContent: "center",
  },
  streakEmoji: { fontSize: 32 },
  streakValue: { color: theme.text, fontSize: 28, fontWeight: "700" },
  streakUnit: { color: theme.textMuted, fontSize: 14, fontWeight: "400" },
  streakLabel: { color: theme.textMuted, fontSize: 12, letterSpacing: 0.5, marginTop: 2 },
  streakBest: { color: theme.primary, fontSize: 11, marginTop: 2, fontStyle: "italic" },
  shareMini: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: theme.border,
  },
  trophyGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  trophyItem: {
    width: "31%",
    backgroundColor: theme.surface,
    borderRadius: 14,
    padding: 12,
    alignItems: "center",
    gap: 8,
    borderWidth: 1,
    borderColor: theme.primary,
  },
  trophyItemLocked: { borderColor: theme.border, opacity: 0.6 },
  trophyIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: theme.primary,
    alignItems: "center",
    justifyContent: "center",
  },
  trophyIconLocked: { backgroundColor: theme.border },
  trophyName: { color: theme.text, fontSize: 11, textAlign: "center", fontWeight: "600" },
  trophyNameLocked: { color: theme.textMuted },
  notifCard: {
    backgroundColor: theme.surface,
    borderRadius: 18,
    padding: 16,
    borderWidth: 1,
    borderColor: theme.border,
  },
  notifHead: { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 14 },
  notifIconWrap: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: theme.primary,
    alignItems: "center",
    justifyContent: "center",
  },
  slotsRow: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 14 },
  slotChip: {
    paddingHorizontal: 12,
    paddingVertical: 7,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: theme.border,
    backgroundColor: theme.bg,
  },
  slotChipOn: { borderColor: theme.primary, backgroundColor: "rgba(212,175,55,0.15)" },
  slotText: { color: theme.textMuted, fontSize: 13, fontWeight: "700", letterSpacing: 0.5 },
  slotTextOn: { color: theme.primary },
  notifBtnRow: { flexDirection: "row", gap: 10 },
  notifBtn: {
    flex: 1,
    backgroundColor: theme.primary,
    paddingVertical: 12,
    borderRadius: 999,
    alignItems: "center",
  },
  notifBtnText: { color: theme.bg, fontWeight: "700", fontSize: 14, letterSpacing: 0.3 },
  notifBtnGhost: { backgroundColor: "transparent", borderWidth: 1, borderColor: theme.border },
  notifBtnGhostText: { color: theme.text, fontWeight: "600", fontSize: 14 },
  notifBtnSmall: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 16,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: theme.border,
  },
  notifBtnSmallText: { color: theme.primary, fontWeight: "600", fontSize: 13 },
  notifHeaderRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 16,
    marginBottom: 6,
  },
  toggle: {
    width: 50,
    height: 28,
    borderRadius: 14,
    backgroundColor: theme.border,
    padding: 3,
    justifyContent: "center",
  },
  toggleOn: { backgroundColor: theme.primary },
  toggleKnob: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: "#fff",
    transform: [{ translateX: 0 }],
  },
  toggleKnobOn: { transform: [{ translateX: 22 }] },
  notifSubtitle: { color: theme.textMuted, fontSize: 13, marginBottom: 16 },
  microLabel: {
    color: theme.textMuted,
    fontSize: 10,
    letterSpacing: 1.5,
    fontWeight: "700",
    marginBottom: 10,
    textTransform: "uppercase",
  },
  windowsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    marginBottom: 14,
  },
  windowBtn: {
    width: "48%",
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingVertical: 12,
    paddingHorizontal: 14,
    borderRadius: 14,
    backgroundColor: theme.surface,
    borderWidth: 1,
    borderColor: theme.border,
  },
  windowBtnOn: { backgroundColor: theme.primary, borderColor: theme.primary },
  windowText: { color: theme.text, fontSize: 13, fontWeight: "600" },
  windowTextOn: { color: theme.bg },
  nextAtRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginBottom: 12,
  },
  nextAtText: { color: theme.textMuted, fontSize: 12 },
});
