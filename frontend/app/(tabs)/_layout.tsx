import { useEffect, useState } from "react";
import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { api, theme } from "../../src/lib/api";
import { TrophyModal, Trophy } from "../../src/components/TrophyModal";
import { useAuth } from "../../src/context/AuthContext";

export default function TabsLayout() {
  const { user, refresh } = useAuth();
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
            height: 78,
            paddingTop: 8,
            paddingBottom: 18,
          },
          tabBarActiveTintColor: theme.primary,
          tabBarInactiveTintColor: theme.textMuted,
          tabBarLabelStyle: { fontSize: 11, letterSpacing: 0.3 },
        }}
      >
        <Tabs.Screen
          name="feed"
          options={{
            title: "Scopri",
            tabBarIcon: ({ color, size }) => <Ionicons name="flame" color={color} size={size} />,
          }}
        />
        <Tabs.Screen
          name="saved"
          options={{
            title: "Salvati",
            tabBarIcon: ({ color, size }) => <Ionicons name="bookmark" color={color} size={size} />,
          }}
        />
        <Tabs.Screen
          name="profile"
          options={{
            title: "Profilo",
            tabBarIcon: ({ color, size }) => <Ionicons name="person-circle" color={color} size={size} />,
          }}
        />
      </Tabs>
      <TrophyModal trophies={newTrophies} onClose={() => setNewTrophies([])} />
    </>
  );
}
