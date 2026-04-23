import { useEffect, useState } from "react";
import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useTranslation } from "react-i18next";
import { api, theme } from "../../src/lib/api";
import { TrophyModal, Trophy } from "../../src/components/TrophyModal";
import { useAuth } from "../../src/context/AuthContext";
import { ensureDefaultScheduling } from "../../src/lib/notifications";

export default function TabsLayout() {
  const { user, refresh } = useAuth();
  const { t } = useTranslation();
  const insets = useSafeAreaInsets();
  const [newTrophies, setNewTrophies] = useState<Trophy[]>([]);

  useEffect(() => {
    if (!user) return;
    (async () => {
      try {
        const res = await api.checkin();
        if (res?.new_trophies?.length) {
          setNewTrophies(res.new_trophies);
        }
        refresh();
      } catch {}
      // Auto-enable 4 daily random reminders (default: Sorpresa window)
      ensureDefaultScheduling().catch(() => {});
    })();
  }, [user?.id]);

  return (
    <>
      <Tabs
        screenOptions={{
          headerShown: false,
          tabBarStyle: {
            backgroundColor: theme.surface,
            borderTopColor: theme.border,
            borderTopWidth: 1,
            height: 62 + Math.max(insets.bottom, 16),
            paddingTop: 8,
            paddingBottom: Math.max(insets.bottom + 8, 24),
          },
          tabBarActiveTintColor: theme.primary,
          tabBarInactiveTintColor: theme.textMuted,
          tabBarLabelStyle: { fontSize: 11, letterSpacing: 0.3 },
        }}
      >
        <Tabs.Screen
          name="feed"
          options={{
            title: t("tabs.feed"),
            tabBarIcon: ({ color, size }) => <Ionicons name="flame" color={color} size={size} />,
          }}
        />
        <Tabs.Screen
          name="saved"
          options={{
            title: t("tabs.saved"),
            tabBarIcon: ({ color, size }) => <Ionicons name="bookmark" color={color} size={size} />,
          }}
        />
        <Tabs.Screen
          name="profile"
          options={{
            title: t("tabs.profile"),
            tabBarIcon: ({ color, size }) => <Ionicons name="person-circle" color={color} size={size} />,
          }}
        />
      </Tabs>
      <TrophyModal trophies={newTrophies} onClose={() => setNewTrophies([])} />
    </>
  );
}
