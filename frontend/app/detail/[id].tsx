import { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Image,
  Dimensions,
  Linking,
  Share,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { api, theme } from "../../src/lib/api";

const { width } = Dimensions.get("window");

type Fact = {
  id: string;
  title: string;
  short_fact: string;
  deep_dive: string;
  category: string;
  image_url: string;
  source: string;
  sources?: { title: string; url: string }[];
  is_liked?: boolean;
  is_bookmarked?: boolean;
};

export default function Detail() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const [fact, setFact] = useState<Fact | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    api
      .fact(id)
      .then((f) => setFact(f))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  const toggleLike = async () => {
    if (!fact) return;
    const newLiked = !fact.is_liked;
    setFact({ ...fact, is_liked: newLiked });
    try {
      await api.react(fact.id, newLiked ? "like" : "dislike");
    } catch {}
  };

  const toggleBookmark = async () => {
    if (!fact) return;
    setFact({ ...fact, is_bookmarked: !fact.is_bookmarked });
    try {
      await api.bookmark(fact.id);
    } catch {}
  };

  const onShare = async () => {
    if (!fact) return;
    try {
      await Share.share({
        message: `Lo sapevi che…\n\n${fact.title}\n\n${fact.short_fact}\n\n— Lo Sapevi che? ✨`,
      });
    } catch {}
  };

  if (loading || !fact) {
    return (
      <View style={styles.loader} testID="detail-loading">
        <ActivityIndicator color={theme.primary} size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container} testID="detail-screen">
      <ScrollView contentContainerStyle={{ paddingBottom: 100 }} showsVerticalScrollIndicator={false}>
        <View style={styles.heroWrap}>
          <Image source={{ uri: fact.image_url }} style={styles.hero} />
          <LinearGradient
            colors={["rgba(5,6,10,0.6)", "transparent", "rgba(5,6,10,1)"]}
            locations={[0, 0.5, 1]}
            style={StyleSheet.absoluteFillObject}
          />
          <SafeAreaView style={styles.heroOverlay} edges={["top"]}>
            <TouchableOpacity style={styles.closeBtn} onPress={() => router.back()} testID="close-detail">
              <Ionicons name="chevron-back" size={22} color={theme.text} />
            </TouchableOpacity>
            <View style={{ flex: 1 }} />
            <View style={styles.heroText}>
              <View style={styles.catPill}>
                <Ionicons name="sparkles" size={12} color={theme.primary} />
                <Text style={styles.catPillText}>{fact.category}</Text>
              </View>
              <Text style={styles.kicker}>Lo sapevi che…</Text>
              <Text style={styles.heroTitle}>{fact.title}</Text>
            </View>
          </SafeAreaView>
        </View>

        <View style={styles.body}>
          <Text style={styles.short}>{fact.short_fact}</Text>

          <View style={styles.divider}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>APPROFONDIMENTO</Text>
            <View style={styles.dividerLine} />
          </View>

          <Text style={styles.deep}>{fact.deep_dive}</Text>

          {fact.sources && fact.sources.length > 0 && (
            <View style={styles.sourcesBox}>
              <Text style={styles.sourcesTitle}>FONTI</Text>
              {fact.sources.map((s, idx) => (
                <TouchableOpacity
                  key={idx}
                  testID={`source-${idx}`}
                  style={styles.sourceRow}
                  onPress={() => Linking.openURL(s.url).catch(() => {})}
                  activeOpacity={0.7}
                >
                  <Ionicons name="link-outline" size={14} color={theme.primary} />
                  <Text style={styles.sourceText} numberOfLines={2}>
                    {s.title}
                  </Text>
                  <Ionicons name="open-outline" size={14} color={theme.textMuted} />
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>
      </ScrollView>

      <SafeAreaView style={styles.bottomBar} edges={["bottom"]}>
        <TouchableOpacity
          testID="detail-like"
          style={[styles.actionBtn, fact.is_liked && styles.actionBtnOn]}
          onPress={toggleLike}
        >
          <Ionicons
            name={fact.is_liked ? "heart" : "heart-outline"}
            size={22}
            color={fact.is_liked ? theme.bg : theme.text}
          />
          <Text style={[styles.actionText, fact.is_liked && styles.actionTextOn]}>
            {fact.is_liked ? "Ti piace" : "Mi piace"}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          testID="detail-bookmark"
          style={styles.iconOnly}
          onPress={toggleBookmark}
        >
          <Ionicons
            name={fact.is_bookmarked ? "bookmark" : "bookmark-outline"}
            size={22}
            color={fact.is_bookmarked ? theme.primary : theme.text}
          />
        </TouchableOpacity>
        <TouchableOpacity testID="detail-share" style={styles.iconOnly} onPress={onShare}>
          <Ionicons name="share-social-outline" size={22} color={theme.text} />
        </TouchableOpacity>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.bg },
  loader: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: theme.bg },
  heroWrap: { height: 460, position: "relative" },
  hero: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, width: "100%", height: "100%" },
  heroOverlay: { flex: 1, padding: 20, justifyContent: "space-between" },
  closeBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "rgba(18,20,29,0.85)",
    alignItems: "center",
    justifyContent: "center",
    alignSelf: "flex-start",
    borderWidth: 1,
    borderColor: theme.border,
  },
  heroText: { gap: 10 },
  catPill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    alignSelf: "flex-start",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: "rgba(18,20,29,0.85)",
    borderWidth: 1,
    borderColor: theme.border,
  },
  catPillText: { color: theme.text, fontSize: 12, fontWeight: "600", letterSpacing: 0.5 },
  kicker: { color: theme.primary, fontSize: 13, letterSpacing: 2, textTransform: "uppercase", fontStyle: "italic" },
  heroTitle: {
    color: theme.text,
    fontSize: 34,
    fontWeight: "300",
    fontStyle: "italic",
    lineHeight: 42,
    letterSpacing: -0.3,
  },
  body: { padding: 24, gap: 18 },
  short: { color: theme.text, fontSize: 18, lineHeight: 28, fontStyle: "italic", fontWeight: "400" },
  divider: { flexDirection: "row", alignItems: "center", gap: 10, marginTop: 14 },
  dividerLine: { flex: 1, height: 1, backgroundColor: theme.border },
  dividerText: { color: theme.primary, fontSize: 11, letterSpacing: 2, fontWeight: "700" },
  deep: { color: theme.textMuted, fontSize: 16, lineHeight: 26 },
  sourcesBox: {
    marginTop: 24,
    padding: 16,
    borderRadius: 14,
    backgroundColor: theme.surface,
    borderWidth: 1,
    borderColor: theme.border,
  },
  sourcesTitle: {
    color: theme.primary,
    fontSize: 11,
    letterSpacing: 2,
    fontWeight: "700",
    marginBottom: 10,
  },
  sourceRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: theme.border,
  },
  sourceText: { color: theme.text, fontSize: 13, flex: 1, textDecorationLine: "underline" },
  bottomBar: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: theme.surface,
    borderTopWidth: 1,
    borderTopColor: theme.border,
    flexDirection: "row",
    padding: 14,
    gap: 10,
  },
  actionBtn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    paddingVertical: 14,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: theme.border,
    backgroundColor: theme.bg,
  },
  actionBtnOn: { backgroundColor: theme.primary, borderColor: theme.primary },
  actionText: { color: theme.text, fontWeight: "600", letterSpacing: 0.3 },
  actionTextOn: { color: theme.bg },
  iconOnly: {
    width: 52,
    height: 52,
    borderRadius: 26,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: theme.border,
    backgroundColor: theme.bg,
  },
});
