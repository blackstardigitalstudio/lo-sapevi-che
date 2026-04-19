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
import * as Device from "expo-device";
import Constants from "expo-constants";
import { useFocusEffect, useRouter } from "expo-router";
import { api, theme } from "../../src/lib/api";
import { useAuth } from "../../src/context/AuthContext";

export default function Profile() {
  const router = useRouter();
  const { user, logout, refresh } = useAuth();
  const [notifStatus, setNotifStatus] = useState<string>("idle");
  const [busy, setBusy] = useState(false);
  const [trophies, setTrophies] = useState<any[]>([]);

  useFocusEffect(
    useCallback(() => {
      refresh();
      api.trophies().then(setTrophies).catch(() => {});
    }, [])
  );

  const shareProfile = async () => {
    if (!user) return;
    try {
      const earned = trophies.filter((t) => t.earned).length;
      await Share.share({
        message: `Sto esplorando il mondo con Lo Sapevi che? 🔮\n\n📖 ${user.stats.seen} curiosità lette\n❤️ ${user.stats.liked} preferite\n🔥 Streak: ${user.streak_days || 0} giorni\n🏆 ${earned} trofei sbloccati\n\nScopri anche tu curiosità affascinanti ogni giorno!`,
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

  const enablePush = async () => {
    setBusy(true);
    setNotifStatus("requesting");
    try {
      if (!Device.isDevice) {
        setNotifStatus("simulator");
        Alert.alert(
          "Dispositivo fisico richiesto",
          "Le notifiche push funzionano solo su dispositivi fisici, non su emulatori."
        );
        return;
      }
      if (Platform.OS === "android") {
        await Notifications.setNotificationChannelAsync("default", {
          name: "Curiosità del giorno",
          importance: Notifications.AndroidImportance.HIGH,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: theme.primary,
        });
      }
      const { status: existing } = await Notifications.getPermissionsAsync();
      let finalStatus = existing;
      if (existing !== "granted") {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      if (finalStatus !== "granted") {
        setNotifStatus("denied");
        Alert.alert("Permesso negato", "Abilita le notifiche dalle impostazioni di sistema.");
        return;
      }
      const projectId =
        (Constants as any)?.expoConfig?.extra?.eas?.projectId ??
        (Constants as any)?.easConfig?.projectId;
      let tokenStr = "";
      try {
        const token = await Notifications.getExpoPushTokenAsync(
          projectId ? { projectId } : undefined
        );
        tokenStr = token.data;
      } catch (e) {
        tokenStr = `local-${user.id}`;
      }
      await api.setPushToken(tokenStr);

      // Schedule daily local notification at 09:00
      await Notifications.cancelAllScheduledNotificationsAsync();
      await Notifications.scheduleNotificationAsync({
        content: {
          title: "Lo Sapevi che?",
          body: "La tua curiosità del giorno ti aspetta ✨",
          sound: "default",
        },
        trigger: {
          type: Notifications.SchedulableTriggerInputTypes.DAILY,
          hour: 9,
          minute: 0,
        } as any,
      });

      setNotifStatus("granted");
      Alert.alert("Notifiche attivate", "Riceverai ogni giorno alle 9:00 una nuova curiosità.");
    } catch (e: any) {
      setNotifStatus("error");
      Alert.alert("Errore", e?.message || "Impossibile attivare le notifiche");
    } finally {
      setBusy(false);
    }
  };

  const testPush = async () => {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: "Lo Sapevi che?",
          body: "Questa è una notifica di prova ✨",
          sound: "default",
        },
        trigger: { type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL, seconds: 3 } as any,
      });
      Alert.alert("Prova inviata", "Riceverai la notifica tra 3 secondi.");
    } catch (e: any) {
      Alert.alert("Errore", e?.message || "Impossibile inviare");
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
          <Stat label="Lette" value={user.stats.seen} />
          <Stat label="Piaciute" value={user.stats.liked} />
          <Stat label="Salvate" value={user.stats.bookmarked} />
        </View>

        <View style={styles.streakCard} testID="streak-card">
          <View style={styles.streakLeft}>
            <Text style={styles.streakEmoji}>🔥</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.streakValue}>
              {user.streak_days || 0} <Text style={styles.streakUnit}>giorni</Text>
            </Text>
            <Text style={styles.streakLabel}>Streak attuale</Text>
            {user.best_streak ? (
              <Text style={styles.streakBest}>Record personale: {user.best_streak}</Text>
            ) : null}
          </View>
          <TouchableOpacity style={styles.shareMini} onPress={shareProfile} testID="share-profile">
            <Ionicons name="share-social-outline" size={20} color={theme.primary} />
          </TouchableOpacity>
        </View>

        <Text style={styles.sectionTitle}>Trofei · {trophies.filter((t) => t.earned).length}/{trophies.length}</Text>
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

        <Text style={styles.sectionTitle}>Top interessi</Text>
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

        <Text style={styles.sectionTitle}>Notifiche giornaliere</Text>
        <View style={styles.actionCard}>
          <View style={{ flex: 1 }}>
            <Text style={styles.actionTitle}>Curiosità quotidiana</Text>
            <Text style={styles.actionSubtitle}>
              Ogni giorno alle 9:00 una nuova perla di sapere
            </Text>
          </View>
          <TouchableOpacity
            testID="enable-push"
            style={styles.actionBtn}
            onPress={enablePush}
            disabled={busy}
          >
            {busy ? (
              <ActivityIndicator color={theme.bg} />
            ) : (
              <Text style={styles.actionBtnText}>
                {notifStatus === "granted" ? "Attivo" : "Attiva"}
              </Text>
            )}
          </TouchableOpacity>
        </View>

        {notifStatus === "granted" && (
          <TouchableOpacity style={styles.ghostBtn} onPress={testPush} testID="test-push">
            <Ionicons name="notifications-outline" size={18} color={theme.primary} />
            <Text style={styles.ghostText}>Prova notifica (3 sec)</Text>
          </TouchableOpacity>
        )}

        <Text style={styles.sectionTitle}>Account</Text>
        <TouchableOpacity
          style={styles.rowBtn}
          onPress={() => router.push("/onboarding")}
          testID="edit-interests"
        >
          <Ionicons name="options-outline" size={20} color={theme.text} />
          <Text style={styles.rowText}>Modifica interessi</Text>
          <Ionicons name="chevron-forward" size={18} color={theme.textMuted} />
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.rowBtn, { borderColor: theme.error }]}
          onPress={() => {
            Alert.alert("Esci", "Vuoi davvero uscire?", [
              { text: "Annulla", style: "cancel" },
              {
                text: "Esci",
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
          <Text style={[styles.rowText, { color: theme.error }]}>Esci</Text>
          <View style={{ width: 18 }} />
        </TouchableOpacity>

        <Text style={styles.version}>Lo Sapevi che? · v1.0</Text>
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
});
