import { useEffect, useRef } from "react";
import { View, StyleSheet, Animated, Dimensions } from "react-native";
import { theme } from "../lib/api";

const { height: SCREEN_H } = Dimensions.get("window");

type Props = {
  height?: number;
};

/**
 * Full-screen shimmering skeleton matching the TikTok-style fact card layout.
 * Used while the initial feed is loading.
 */
export function FeedSkeleton({ height: h = SCREEN_H - 100 }: Props) {
  const shimmer = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(shimmer, { toValue: 1, duration: 900, useNativeDriver: true }),
        Animated.timing(shimmer, { toValue: 0, duration: 900, useNativeDriver: true }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [shimmer]);

  const opacity = shimmer.interpolate({ inputRange: [0, 1], outputRange: [0.35, 0.7] });

  return (
    <View style={[styles.card, { height: h }]} testID="feed-skeleton">
      <Animated.View style={[styles.image, { opacity }]} />
      <View style={styles.topRow}>
        <Animated.View style={[styles.pill, { opacity }]} />
      </View>
      <View style={styles.bottom}>
        <Animated.View style={[styles.kicker, { opacity }]} />
        <Animated.View style={[styles.titleLine, { opacity }]} />
        <Animated.View style={[styles.titleLine, { width: "80%", opacity }]} />
        <Animated.View style={[styles.titleLine, { width: "60%", opacity }]} />
        <Animated.View style={[styles.shortLine, { opacity }]} />
        <Animated.View style={[styles.shortLine, { width: "70%", opacity }]} />
        <View style={styles.actionsRow}>
          <Animated.View style={[styles.discoverBtn, { opacity }]} />
          <View style={styles.iconsRow}>
            <Animated.View style={[styles.iconDot, { opacity }]} />
            <Animated.View style={[styles.iconDot, { opacity }]} />
            <Animated.View style={[styles.iconDot, { opacity }]} />
            <Animated.View style={[styles.iconDot, { opacity }]} />
          </View>
        </View>
      </View>
    </View>
  );
}

const shimmerColor = theme.surfaceAlt;

const styles = StyleSheet.create({
  card: {
    width: "100%",
    backgroundColor: theme.bg,
    padding: 20,
    justifyContent: "space-between",
    position: "relative",
  },
  image: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: theme.surface,
  },
  topRow: { flexDirection: "row", zIndex: 2 },
  pill: {
    width: 100,
    height: 28,
    borderRadius: 14,
    backgroundColor: shimmerColor,
  },
  bottom: { marginBottom: 80, zIndex: 2 },
  kicker: {
    width: 140,
    height: 14,
    borderRadius: 4,
    backgroundColor: shimmerColor,
    marginBottom: 14,
  },
  titleLine: {
    height: 32,
    borderRadius: 6,
    backgroundColor: shimmerColor,
    marginBottom: 8,
    width: "95%",
  },
  shortLine: {
    height: 18,
    borderRadius: 4,
    backgroundColor: shimmerColor,
    marginTop: 14,
    width: "90%",
  },
  actionsRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 26,
  },
  discoverBtn: {
    width: 140,
    height: 44,
    borderRadius: 999,
    backgroundColor: shimmerColor,
  },
  iconsRow: { flexDirection: "row", gap: 8 },
  iconDot: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: shimmerColor,
  },
});
