import { useCallback, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Image,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useFocusEffect, useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { api, theme } from "../../src/lib/api";

type Fact = {
  id: string;
  title: string;
  short_fact: string;
  category: string;
  image_url: string;
};

export default function Saved() {
  const router = useRouter();
  const [facts, setFacts] = useState<Fact[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = async () => {
    try {
      const res = await api.bookmarks();
      setFacts(res.facts);
    } catch {} finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      load();
    }, [])
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.loader} testID="saved-loading">
        <ActivityIndicator color={theme.primary} size="large" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} testID="saved-screen" edges={["top"]}>
      <View style={styles.header}>
        <Text style={styles.kicker}>La tua collezione</Text>
        <Text style={styles.title}>Salvati</Text>
      </View>

      <FlatList
        data={facts}
        keyExtractor={(it) => it.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => {
              setRefreshing(true);
              load();
            }}
            tintColor={theme.primary}
          />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="bookmark-outline" size={42} color={theme.primary} />
            <Text style={styles.emptyTitle}>Nessun salvato</Text>
            <Text style={styles.emptyText}>
              Tocca l'icona segnalibro su una curiosità per salvarla qui.
            </Text>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            testID={`saved-card-${item.id}`}
            style={styles.card}
            onPress={() => router.push(`/detail/${item.id}`)}
            activeOpacity={0.85}
          >
            <Image source={{ uri: item.image_url }} style={styles.thumb} />
            <View style={styles.cardBody}>
              <Text style={styles.cat}>{item.category.toUpperCase()}</Text>
              <Text style={styles.cardTitle} numberOfLines={2}>
                {item.title}
              </Text>
              <Text style={styles.cardExcerpt} numberOfLines={2}>
                {item.short_fact}
              </Text>
            </View>
          </TouchableOpacity>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.bg },
  loader: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: theme.bg },
  header: { padding: 24, paddingBottom: 8 },
  kicker: { color: theme.primary, fontSize: 12, letterSpacing: 1.5, textTransform: "uppercase", fontStyle: "italic" },
  title: { color: theme.text, fontSize: 34, fontWeight: "300", fontStyle: "italic", marginTop: 6 },
  list: { padding: 16, paddingBottom: 100 },
  empty: { marginTop: 80, alignItems: "center", padding: 24, gap: 10 },
  emptyTitle: { color: theme.text, fontSize: 20, fontWeight: "300", fontStyle: "italic" },
  emptyText: { color: theme.textMuted, textAlign: "center" },
  card: {
    flexDirection: "row",
    backgroundColor: theme.surface,
    borderRadius: 18,
    overflow: "hidden",
    marginBottom: 14,
    borderWidth: 1,
    borderColor: theme.border,
  },
  thumb: { width: 110, height: 130 },
  cardBody: { flex: 1, padding: 14, justifyContent: "center", gap: 6 },
  cat: { color: theme.primary, fontSize: 10, letterSpacing: 1.5, fontWeight: "700" },
  cardTitle: { color: theme.text, fontSize: 15, fontWeight: "500", lineHeight: 21 },
  cardExcerpt: { color: theme.textMuted, fontSize: 12, lineHeight: 17 },
});
