import { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAuth } from "../src/context/AuthContext";
import { api, theme } from "../src/lib/api";
import { Ionicons } from "@expo/vector-icons";

type Category = { name: string; icon: string };

export default function Onboarding() {
  const router = useRouter();
  const { user, refresh } = useAuth();
  const [cats, setCats] = useState<Category[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set(user?.interests || []));
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.categories().then(setCats).catch(() => {});
  }, []);

  const toggle = (name: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const onContinue = async () => {
    if (selected.size < 3) return;
    setSaving(true);
    try {
      await api.updateInterests(Array.from(selected));
      await refresh();
      router.replace("/(tabs)/feed");
    } catch {
    } finally {
      setSaving(false);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={["top"]} testID="onboarding-screen">
      <View style={styles.header}>
        <Text style={styles.greet}>Ciao {user?.name} 👋</Text>
        <Text style={styles.title}>Cosa ti affascina?</Text>
        <Text style={styles.subtitle}>
          Scegli almeno 3 nicchie. Le useremo per personalizzare le tue curiosità quotidiane.
        </Text>
      </View>

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <View style={styles.chipsWrap}>
          {cats.map((c) => {
            const on = selected.has(c.name);
            return (
              <TouchableOpacity
                key={c.name}
                testID={`chip-${c.name}`}
                style={[styles.chip, on && styles.chipOn]}
                onPress={() => toggle(c.name)}
                activeOpacity={0.8}
              >
                <Ionicons
                  name={c.icon as any}
                  size={16}
                  color={on ? theme.bg : theme.textMuted}
                  style={{ marginRight: 6 }}
                />
                <Text style={[styles.chipText, on && styles.chipTextOn]}>{c.name}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </ScrollView>

      <View style={styles.bottom}>
        <Text style={styles.counter}>
          {selected.size < 3
            ? `Seleziona almeno ${3 - selected.size} in più`
            : `${selected.size} nicchie selezionate`}
        </Text>
        <TouchableOpacity
          testID="onboarding-continue"
          style={[styles.cta, selected.size < 3 && styles.ctaDisabled]}
          disabled={selected.size < 3 || saving}
          onPress={onContinue}
        >
          {saving ? (
            <ActivityIndicator color={theme.bg} />
          ) : (
            <Text style={styles.ctaText}>Inizia l'avventura</Text>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.bg },
  header: { paddingHorizontal: 24, paddingTop: 16, paddingBottom: 8 },
  greet: { color: theme.textMuted, fontSize: 14, letterSpacing: 0.5 },
  title: { color: theme.text, fontSize: 36, fontWeight: "300", fontStyle: "italic", marginTop: 8, letterSpacing: -0.5 },
  subtitle: { color: theme.textMuted, fontSize: 14, marginTop: 12, lineHeight: 20 },
  scroll: { padding: 24 },
  chipsWrap: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  chip: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: theme.border,
    backgroundColor: "transparent",
  },
  chipOn: { backgroundColor: theme.primary, borderColor: theme.primary },
  chipText: { color: theme.textMuted, fontSize: 14, fontWeight: "500" },
  chipTextOn: { color: theme.bg, fontWeight: "700" },
  bottom: {
    padding: 24,
    borderTopWidth: 1,
    borderTopColor: theme.border,
    backgroundColor: theme.surface,
  },
  counter: { color: theme.textMuted, textAlign: "center", marginBottom: 12, fontSize: 13 },
  cta: {
    backgroundColor: theme.primary,
    borderRadius: 999,
    paddingVertical: 16,
    alignItems: "center",
  },
  ctaDisabled: { opacity: 0.4 },
  ctaText: { color: theme.bg, fontWeight: "700", fontSize: 16, letterSpacing: 0.5 },
});
