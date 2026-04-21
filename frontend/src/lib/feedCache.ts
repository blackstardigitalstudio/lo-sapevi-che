import AsyncStorage from "@react-native-async-storage/async-storage";

const FEED_CACHE_KEY = "@losapevi_feed_cache_v1";
const MAX_CACHED = 50;

export type CachedFact = {
  id: string;
  title: string;
  short_fact: string;
  deep_dive: string;
  category: string;
  image_url: string;
  source: string;
};

export async function saveFeedCache(facts: CachedFact[]): Promise<void> {
  try {
    const trimmed = facts.slice(0, MAX_CACHED);
    await AsyncStorage.setItem(
      FEED_CACHE_KEY,
      JSON.stringify({ facts: trimmed, savedAt: Date.now() }),
    );
  } catch {
    // ignore cache failures silently
  }
}

export async function loadFeedCache(): Promise<{
  facts: CachedFact[];
  savedAt: number | null;
}> {
  try {
    const raw = await AsyncStorage.getItem(FEED_CACHE_KEY);
    if (!raw) return { facts: [], savedAt: null };
    const parsed = JSON.parse(raw);
    return {
      facts: Array.isArray(parsed?.facts) ? parsed.facts : [],
      savedAt: typeof parsed?.savedAt === "number" ? parsed.savedAt : null,
    };
  } catch {
    return { facts: [], savedAt: null };
  }
}

export async function clearFeedCache(): Promise<void> {
  try {
    await AsyncStorage.removeItem(FEED_CACHE_KEY);
  } catch {}
}
