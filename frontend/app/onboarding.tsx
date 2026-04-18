import { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  ImageBackground,
} from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../src/context/AuthContext";
import { api, theme } from "../src/lib/api";

type Preview = {
  category: string;
  icon: string;
  sample_title: string;
  sample_short: string;
  image_url: string;
};

export default function Onboarding() {
  const router = useRouter();
  const { user, refresh } = useAuth();
  const [previews, setPreviews] = useState<Preview[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Set<string>>(new Set(user?.interests || []));
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api
      .preview()
      .then(setPreviews)
      .catch(() => {})
      .finally(() => setLoading(false));
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

  if (loading) {
    return (
      <View style={styles.loader}>
        <ActivityIndicator color={theme.primary} />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={["top"]} testID="onboarding-screen">
      <View style={styles.header}>
        <Text style={styles.greet}>Ciao {user?.name} 👋</Text>
        <Text style={styles.title}>Cosa ti affascina?</Text>
        <Text style={styles.subtitle}>
          Tocca le card per scegliere almeno 3 nicchie. Personalizzeremo il tuo feed con curiosità su misura.
        </Text>
      </View>

      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.grid}>
          {previews.map((p) => {
            const on = selected.has(p.category);
            return (
              <TouchableOpacity
                key={p.category}
                testID={`chip-${p.category}`}
                activeOpacity={0.85}
                style={[styles.card, on && styles.cardOn]}
                onPress={() => toggle(p.category)}
              >
                <ImageBackground source={{ uri: p.image_url }} style={styles.cardBg}>
                  <LinearGradient
                    colors={["rgba(5,6,10,0.45)", "rgba(5,6,10,0.95)"]}
                    locations={[0, 1]}
                    style={StyleSheet.absoluteFillObject}
                  />
                  <View style={styles.cardContent}>
                    <View style={styles.iconRow}>
                      <Ionicons name={p.icon as any} size={18} color={on ? theme.primary : theme.text} />
                      <Text style={[styles.cardCat, on && styles.cardCatOn]}>{p.category}</Text>
                      <View style={styles.checkbox}>
                        {on && <Ionicons name="checkmark" size={14} color={theme.bg} />}
                      </View>
                    </View>
                    <Text style={styles.sampleKicker}>Lo sapevi che…</Text>
                    <Text style={styles.sampleTitle} numberOfLines={3}>
                      {p.sample_title}
                    </Text>
                  </View>
                </ImageBackground>
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
          {saving ? <ActivityIndicator color={theme.bg} /> : <Text style={styles.ctaText}>Inizia l'avventura</Text>}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.bg },
  loader: { flex: 1, backgroundColor: theme.bg, alignItems: "center", justifyContent: "center" },
  header: { paddingHorizontal: 24, paddingTop: 16, paddingBottom: 8 },
  greet: { color: theme.textMuted, fontSize: 14, letterSpacing: 0.5 },
  title: { color: theme.text, fontSize: 36, fontWeight: "300", fontStyle: "italic", marginTop: 8, letterSpacing: -0.5 },
  subtitle: { color: theme.textMuted, fontSize: 14, marginTop: 12, lineHeight: 20 },
  scroll: { padding: 16, paddingBottom: 32 },
  grid: { flexDirection: "row", flexWrap: "wrap", justifyContent: "space-between" },
  card: {
    width: "48.5%",
    aspectRatio: 0.82,
    borderRadius: 18,
    overflow: "hidden",
    marginBottom: 12,
    borderWidth: 2,
    borderColor: theme.border,
  },
  cardOn: { borderColor: theme.primary },
  cardBg: { flex: 1, padding: 12, justifyContent: "flex-end" },
  cardContent: { gap: 4 },
  iconRow: { flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 8 },
  cardCat: { color: theme.text, fontSize: 13, fontWeight: "700", letterSpacing: 0.3, flex: 1 },
  cardCatOn: { color: theme.primary },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: theme.primary,
    alignItems: "center",
    justifyContent: "center",
    opacity: 1,
  },
  sampleKicker: { color: theme.primary, fontSize: 9, letterSpacing: 1.5, textTransform: "uppercase", fontStyle: "italic" },
  sampleTitle: { color: theme.text, fontSize: 12, lineHeight: 16, fontWeight: "400", fontStyle: "italic" },
  bottom: { padding: 20, borderTopWidth: 1, borderTopColor: theme.border, backgroundColor: theme.surface },
  counter: { color: theme.textMuted, textAlign: "center", marginBottom: 12, fontSize: 13 },
  cta: { backgroundColor: theme.primary, borderRadius: 999, paddingVertical: 16, alignItems: "center" },
  ctaDisabled: { opacity: 0.4 },
  ctaText: { color: theme.bg, fontWeight: "700", fontSize: 16, letterSpacing: 0.5 },
});
