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
import { SafeAreaView, useSafeAreaInsets } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../src/context/AuthContext";
import { api, theme } from "../src/lib/api";
import { useTranslation } from "react-i18next";

type Preview = {
  category: string;
  icon: string;
  sample_title: string;
  sample_short: string;
  image_url: string;
};

type CategoryInfo = {
  name: string;
  icon: string;
  has_subcategories: boolean;
  subcategories: string[];
};

export default function Onboarding() {
  const router = useRouter();
  const { t } = useTranslation();
  const { user, refresh } = useAuth();
  const insets = useSafeAreaInsets();
  const [previews, setPreviews] = useState<Preview[]>([]);
  const [catInfo, setCatInfo] = useState<Record<string, CategoryInfo>>({});
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Set<string>>(new Set(user?.interests || []));
  const [subInterests, setSubInterests] = useState<Record<string, Set<string>>>(() => {
    const initial: Record<string, Set<string>> = {};
    if (user?.sub_interests) {
      Object.entries(user.sub_interests).forEach(([k, v]) => {
        initial[k] = new Set(v as string[]);
      });
    }
    return initial;
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([api.preview(), api.categories()])
      .then(([pv, cats]) => {
        setPreviews(pv);
        const info: Record<string, CategoryInfo> = {};
        (cats as CategoryInfo[]).forEach((c) => {
          info[c.name] = c;
        });
        setCatInfo(info);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const toggleCategory = (name: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
        // Also clear sub_interests for this category
        setSubInterests((si) => {
          const n = { ...si };
          delete n[name];
          return n;
        });
      } else {
        next.add(name);
      }
      return next;
    });
  };

  const toggleSub = (cat: string, sub: string) => {
    setSubInterests((prev) => {
      const next = { ...prev };
      const cur = new Set(next[cat] || []);
      if (cur.has(sub)) cur.delete(sub);
      else cur.add(sub);
      next[cat] = cur;
      return next;
    });
  };

  const onContinue = async () => {
    if (selected.size < 3) return;
    setSaving(true);
    try {
      await api.updateInterests(Array.from(selected));
      const subPayload: Record<string, string[]> = {};
      Object.keys(subInterests).forEach((cat) => {
        if (selected.has(cat)) {
          subPayload[cat] = Array.from(subInterests[cat]);
        }
      });
      await api.updateSubInterests(subPayload);
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

  // Selected categories that have subcategories → show drill-down below
  const drillDownCategories = Array.from(selected).filter(
    (c) => catInfo[c]?.has_subcategories,
  );

  return (
    <SafeAreaView style={styles.container} edges={["top"]} testID="onboarding-screen">
      <View style={styles.header}>
        <Text style={styles.greet}>{t("onboarding.hello", { name: user?.name })}</Text>
        <Text style={styles.title}>{t("onboarding.title")}</Text>
        <Text style={styles.subtitle}>{t("onboarding.subtitle")}</Text>
      </View>

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <View style={styles.grid}>
          {previews.map((p) => {
            const on = selected.has(p.category);
            const hasSubs = catInfo[p.category]?.has_subcategories;
            return (
              <TouchableOpacity
                key={p.category}
                testID={`chip-${p.category}`}
                activeOpacity={0.85}
                style={[styles.card, on && styles.cardOn]}
                onPress={() => toggleCategory(p.category)}
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
                    {hasSubs && (
                      <View style={styles.filterHint}>
                        <Ionicons name="options" size={10} color={theme.primary} />
                        <Text style={styles.filterHintText}>con filtri</Text>
                      </View>
                    )}
                  </View>
                </ImageBackground>
              </TouchableOpacity>
            );
          })}
        </View>

        {drillDownCategories.length > 0 && (
          <View style={styles.drillWrap} testID="drilldown-section">
            <Text style={styles.drillTitle}>Affina i tuoi gusti</Text>
            <Text style={styles.drillSubtitle}>
              Lascia vuoto per vedere tutto, oppure scegli i preferiti
            </Text>

            {drillDownCategories.map((cat) => {
              const subs = catInfo[cat]?.subcategories || [];
              const picked = subInterests[cat] || new Set();
              const allMode = picked.size === 0;
              return (
                <View key={cat} style={styles.drillBlock}>
                  <Text style={styles.drillCatName}>
                    <Ionicons name={catInfo[cat]?.icon as any} size={14} color={theme.primary} />
                    {"  "}
                    {cat}
                  </Text>
                  <View style={styles.subChipsRow}>
                    <TouchableOpacity
                      testID={`sub-${cat}-all`}
                      style={[styles.subChip, allMode && styles.subChipOn]}
                      onPress={() =>
                        setSubInterests((p) => {
                          const n = { ...p };
                          delete n[cat];
                          return n;
                        })
                      }
                    >
                      <Text style={[styles.subChipText, allMode && styles.subChipTextOn]}>
                        Tutti
                      </Text>
                    </TouchableOpacity>
                    {subs.map((s) => {
                      const on = picked.has(s);
                      return (
                        <TouchableOpacity
                          key={s}
                          testID={`sub-${cat}-${s}`}
                          style={[styles.subChip, on && styles.subChipOn]}
                          onPress={() => toggleSub(cat, s)}
                        >
                          <Text style={[styles.subChipText, on && styles.subChipTextOn]}>
                            {s}
                          </Text>
                        </TouchableOpacity>
                      );
                    })}
                  </View>
                </View>
              );
            })}
          </View>
        )}
      </ScrollView>

      <View style={[styles.bottom, { paddingBottom: Math.max(insets.bottom + 20, 56) }]}>
        <Text style={styles.counter}>
          {selected.size < 3
            ? t("onboarding.selectMore", { n: 3 - selected.size })
            : t("onboarding.selectedCount", { n: selected.size })}
        </Text>
        <TouchableOpacity
          testID="onboarding-continue"
          style={[styles.cta, selected.size < 3 && styles.ctaDisabled]}
          disabled={selected.size < 3 || saving}
          onPress={onContinue}
        >
          {saving ? <ActivityIndicator color={theme.bg} /> : <Text style={styles.ctaText}>{t("onboarding.startAdventure")}</Text>}
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
  },
  sampleKicker: { color: theme.primary, fontSize: 9, letterSpacing: 1.5, textTransform: "uppercase", fontStyle: "italic" },
  sampleTitle: { color: theme.text, fontSize: 12, lineHeight: 16, fontWeight: "400", fontStyle: "italic" },
  filterHint: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginTop: 6,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 999,
    backgroundColor: "rgba(212,175,55,0.2)",
    alignSelf: "flex-start",
  },
  filterHintText: { color: theme.primary, fontSize: 9, fontWeight: "700", letterSpacing: 0.5 },
  drillWrap: {
    marginTop: 16,
    padding: 18,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: theme.primary,
    backgroundColor: theme.surface,
  },
  drillTitle: { color: theme.primary, fontSize: 13, letterSpacing: 2, fontWeight: "700", marginBottom: 4 },
  drillSubtitle: { color: theme.textMuted, fontSize: 12, marginBottom: 14 },
  drillBlock: { marginTop: 14 },
  drillCatName: { color: theme.text, fontSize: 14, fontWeight: "600", marginBottom: 8 },
  subChipsRow: { flexDirection: "row", flexWrap: "wrap", gap: 6 },
  subChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: theme.border,
    backgroundColor: "transparent",
  },
  subChipOn: { backgroundColor: theme.primary, borderColor: theme.primary },
  subChipText: { color: theme.textMuted, fontSize: 12, fontWeight: "500" },
  subChipTextOn: { color: theme.bg, fontWeight: "700" },
  bottom: { padding: 20, borderTopWidth: 1, borderTopColor: theme.border, backgroundColor: theme.surface },
  counter: { color: theme.textMuted, textAlign: "center", marginBottom: 12, fontSize: 13 },
  cta: { backgroundColor: theme.primary, borderRadius: 999, paddingVertical: 16, alignItems: "center" },
  ctaDisabled: { opacity: 0.4 },
  ctaText: { color: theme.bg, fontWeight: "700", fontSize: 16, letterSpacing: 0.5 },
});
