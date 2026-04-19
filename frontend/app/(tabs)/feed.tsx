import { useCallback, useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  Dimensions,
  ImageBackground,
  TouchableOpacity,
  ActivityIndicator,
  Animated,
  RefreshControl,
  Share,
  useWindowDimensions,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { useRouter } from "expo-router";
import { api, theme } from "../../src/lib/api";
import { useAuth } from "../../src/context/AuthContext";
import { TrophyModal, Trophy } from "../../src/components/TrophyModal";

const { height } = Dimensions.get("window");

type Fact = {
  id: string;
  title: string;
  short_fact: string;
  deep_dive: string;
  category: string;
  image_url: string;
  source: string;
};

export default function Feed() {
  const router = useRouter();
  const { refresh: refreshUser } = useAuth();
  const { height: winH } = useWindowDimensions();
  const TAB_BAR = 78;
  const defaultH = Math.max(400, winH - TAB_BAR);
  const [facts, setFacts] = useState<Fact[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [liked, setLiked] = useState<Set<string>>(new Set());
  const [bookmarked, setBookmarked] = useState<Set<string>>(new Set());
  const [cardHeight, setCardHeight] = useState(defaultH);
  const [generating, setGenerating] = useState(false);
  const [newTrophies, setNewTrophies] = useState<Trophy[]>([]);

  const onShareFact = async (fact: Fact) => {
    try {
      Haptics.selectionAsync();
      await Share.share({
        message: `Lo sapevi che…\n\n${fact.title}\n\n${fact.short_fact}\n\n— condiviso da Lo Sapevi che? ✨`,
      });
    } catch {}
  };

  const loadFeed = useCallback(async () => {
    try {
      const res = await api.feed(20);
      setFacts(res.facts);
    } catch {
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadFeed();
  }, [loadFeed]);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadFeed();
  };

  const onLike = async (fact: Fact) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch {}
    setLiked((p) => new Set(p).add(fact.id));
    try {
      const res = await api.react(fact.id, "like");
      if (res?.new_trophies?.length) setNewTrophies(res.new_trophies);
      refreshUser();
    } catch {}
  };

  const onDislike = async (fact: Fact) => {
    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    } catch {}
    try {
      await api.react(fact.id, "dislike");
      // remove from feed
      setFacts((prev) => prev.filter((f) => f.id !== fact.id));
      refreshUser();
    } catch {}
  };

  const onBookmark = async (fact: Fact) => {
    try {
      Haptics.selectionAsync();
    } catch {}
    const wasBookmarked = bookmarked.has(fact.id);
    setBookmarked((p) => {
      const n = new Set(p);
      if (wasBookmarked) n.delete(fact.id);
      else n.add(fact.id);
      return n;
    });
    try {
      const res = await api.bookmark(fact.id);
      if (res?.new_trophies?.length) setNewTrophies(res.new_trophies);
      refreshUser();
    } catch {}
  };

  const onGenerate = async () => {
    setGenerating(true);
    try {
      const fact = await api.generate();
      setFacts((prev) => [fact, ...prev]);
      if (fact?.new_trophies?.length) setNewTrophies(fact.new_trophies);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch {}
    setGenerating(false);
  };

  const renderItem = ({ item }: { item: Fact }) => {
    const isLiked = liked.has(item.id);
    const isBookmarked = bookmarked.has(item.id);
    return (
      <DoubleTapCard
        fact={item}
        height={cardHeight}
        isLiked={isLiked}
        isBookmarked={isBookmarked}
        onDoubleTap={() => !isLiked && onLike(item)}
        onLike={() => onLike(item)}
        onDislike={() => onDislike(item)}
        onBookmark={() => onBookmark(item)}
        onShare={() => onShareFact(item)}
        onOpen={() => router.push(`/detail/${item.id}`)}
      />
    );
  };

  if (loading) {
    return (
      <View style={styles.loader} testID="feed-loading">
        <ActivityIndicator size="large" color={theme.primary} />
      </View>
    );
  }

  return (
    <View
      style={styles.container}
      testID="feed-screen"
      onLayout={(e) => {
        const h = e.nativeEvent.layout.height;
        if (h > 0 && Math.abs(h - cardHeight) > 1) setCardHeight(h);
      }}
    >
      <FlatList
        data={facts}
        keyExtractor={(it) => it.id}
        renderItem={renderItem}
        pagingEnabled
        showsVerticalScrollIndicator={false}
        snapToInterval={cardHeight}
        snapToAlignment="start"
        decelerationRate="fast"
        disableIntervalMomentum
        getItemLayout={(_, index) => ({
          length: cardHeight,
          offset: cardHeight * index,
          index,
        })}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={theme.primary}
          />
        }
        ListEmptyComponent={
          <View style={[styles.empty, { height: cardHeight }]}>
            <Ionicons name="sparkles-outline" size={48} color={theme.primary} />
            <Text style={styles.emptyTitle}>Hai letto tutto!</Text>
            <Text style={styles.emptyText}>
              Tocca il pulsante ✨ per generare nuove curiosità con l'AI
            </Text>
          </View>
        }
      />

      <SafeAreaView style={styles.fabWrap} pointerEvents="box-none" edges={["top"]}>
        <TouchableOpacity
          testID="generate-ai-btn"
          style={styles.fab}
          onPress={onGenerate}
          disabled={generating}
          activeOpacity={0.8}
        >
          {generating ? (
            <ActivityIndicator color={theme.bg} />
          ) : (
            <Ionicons name="sparkles" size={22} color={theme.bg} />
          )}
        </TouchableOpacity>
      </SafeAreaView>

      <TrophyModal trophies={newTrophies} onClose={() => setNewTrophies([])} />
    </View>
  );
}

function DoubleTapCard({
  fact,
  height: h,
  isLiked,
  isBookmarked,
  onDoubleTap,
  onLike,
  onDislike,
  onBookmark,
  onShare,
  onOpen,
}: {
  fact: Fact;
  height: number;
  isLiked: boolean;
  isBookmarked: boolean;
  onDoubleTap: () => void;
  onLike: () => void;
  onDislike: () => void;
  onBookmark: () => void;
  onShare: () => void;
  onOpen: () => void;
}) {
  const lastTap = useRef(0);
  const heartScale = useRef(new Animated.Value(0)).current;

  const showHeart = () => {
    heartScale.setValue(0);
    Animated.sequence([
      Animated.spring(heartScale, { toValue: 1, useNativeDriver: true, friction: 4 }),
      Animated.delay(300),
      Animated.timing(heartScale, { toValue: 0, duration: 200, useNativeDriver: true }),
    ]).start();
  };

  const onPress = () => {
    const now = Date.now();
    if (now - lastTap.current < 280) {
      onDoubleTap();
      showHeart();
      lastTap.current = 0;
    } else {
      lastTap.current = now;
    }
  };

  // Mark seen when card is first rendered
  useEffect(() => {
    api.markSeen(fact.id).catch(() => {});
  }, [fact.id]);

  return (
    <TouchableOpacity
      activeOpacity={1}
      onPress={onPress}
      style={{ height: h, width: "100%" }}
      testID={`fact-card-${fact.id}`}
    >
      <ImageBackground source={{ uri: fact.image_url }} style={styles.bg} resizeMode="cover">
        <LinearGradient
          colors={["rgba(5,6,10,0.5)", "rgba(5,6,10,0.15)", "rgba(5,6,10,0.95)"]}
          locations={[0, 0.45, 1]}
          style={StyleSheet.absoluteFillObject}
        />

        <SafeAreaView style={styles.cardContent} edges={["top", "bottom"]}>
          {/* Top: category pill */}
          <View style={styles.topRow}>
            <View style={styles.pill}>
              <Ionicons name="sparkles" size={12} color={theme.primary} />
              <Text style={styles.pillText}>{fact.category}</Text>
            </View>
            {fact.source === "ai" && (
              <View style={[styles.pill, styles.pillAi]}>
                <Text style={styles.pillText}>✨ AI</Text>
              </View>
            )}
          </View>

          {/* Heart anim */}
          <View style={styles.heartCenter} pointerEvents="none">
            <Animated.View style={{ transform: [{ scale: heartScale }] }}>
              <Ionicons name="heart" size={140} color={theme.primary} />
            </Animated.View>
          </View>

          {/* Bottom content */}
          <View style={styles.bottomContent}>
            <Text style={styles.kicker}>Lo sapevi che…</Text>
            <Text style={styles.title} numberOfLines={4}>
              {fact.title}
            </Text>
            <Text style={styles.short} numberOfLines={3}>
              {fact.short_fact}
            </Text>

            <View style={styles.actions}>
              <TouchableOpacity
                testID={`discover-${fact.id}`}
                style={styles.discoverBtn}
                onPress={onOpen}
              >
                <Text style={styles.discoverText}>Scopri di più</Text>
                <Ionicons name="arrow-forward" size={16} color={theme.bg} />
              </TouchableOpacity>

              <View style={styles.sideActions}>
                <TouchableOpacity
                  testID={`like-${fact.id}`}
                  style={styles.iconBtn}
                  onPress={onLike}
                >
                  <Ionicons
                    name={isLiked ? "heart" : "heart-outline"}
                    size={26}
                    color={isLiked ? theme.primary : theme.text}
                  />
                </TouchableOpacity>
                <TouchableOpacity
                  testID={`dislike-${fact.id}`}
                  style={styles.iconBtn}
                  onPress={onDislike}
                >
                  <Ionicons name="thumbs-down-outline" size={24} color={theme.text} />
                </TouchableOpacity>
                <TouchableOpacity
                  testID={`bookmark-${fact.id}`}
                  style={styles.iconBtn}
                  onPress={onBookmark}
                >
                  <Ionicons
                    name={isBookmarked ? "bookmark" : "bookmark-outline"}
                    size={24}
                    color={isBookmarked ? theme.primary : theme.text}
                  />
                </TouchableOpacity>
                <TouchableOpacity
                  testID={`share-${fact.id}`}
                  style={styles.iconBtn}
                  onPress={onShare}
                >
                  <Ionicons name="share-social-outline" size={24} color={theme.text} />
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </SafeAreaView>
      </ImageBackground>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.bg },
  loader: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: theme.bg },
  bg: { flex: 1, width: "100%", height: "100%" },
  cardContent: { flex: 1, padding: 20, justifyContent: "space-between" },
  topRow: { flexDirection: "row", gap: 8, alignItems: "center" },
  pill: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    backgroundColor: "rgba(18,20,29,0.85)",
    borderWidth: 1,
    borderColor: theme.border,
  },
  pillAi: { borderColor: theme.primary },
  pillText: { color: theme.text, fontSize: 12, fontWeight: "600", letterSpacing: 0.5 },
  heartCenter: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, alignItems: "center", justifyContent: "center" },
  bottomContent: { marginBottom: 80 },
  kicker: {
    color: theme.primary,
    fontSize: 13,
    letterSpacing: 2,
    textTransform: "uppercase",
    fontStyle: "italic",
    marginBottom: 10,
  },
  title: {
    color: theme.text,
    fontSize: 30,
    fontWeight: "300",
    fontStyle: "italic",
    lineHeight: 38,
    letterSpacing: -0.3,
    marginBottom: 14,
  },
  short: { color: theme.textMuted, fontSize: 15, lineHeight: 22, marginBottom: 20 },
  actions: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 12 },
  discoverBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    backgroundColor: theme.primary,
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 999,
  },
  discoverText: { color: theme.bg, fontWeight: "700", fontSize: 14, letterSpacing: 0.3 },
  sideActions: { flexDirection: "row", gap: 8 },
  iconBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "rgba(18,20,29,0.85)",
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: theme.border,
  },
  empty: { alignItems: "center", justifyContent: "center", padding: 32, gap: 12 },
  emptyTitle: { color: theme.text, fontSize: 22, fontWeight: "300", fontStyle: "italic" },
  emptyText: { color: theme.textMuted, textAlign: "center" },
  fabWrap: {
    position: "absolute",
    top: 0,
    right: 0,
  },
  fab: {
    margin: 20,
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: theme.primary,
    alignItems: "center",
    justifyContent: "center",
    shadowColor: theme.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 8,
  },
});
