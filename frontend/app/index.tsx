import { useEffect } from "react";
import { View, ActivityIndicator, StyleSheet } from "react-native";
import { useRouter } from "expo-router";
import { useAuth } from "../src/context/AuthContext";
import { theme } from "../src/lib/api";

export default function Index() {
  const router = useRouter();
  const { user } = useAuth();

  useEffect(() => {
    if (user === undefined) return;
    if (user === null) {
      router.replace("/auth/login");
    } else if (!user.interests || user.interests.length === 0) {
      router.replace("/onboarding");
    } else {
      router.replace("/(tabs)/feed");
    }
  }, [user]);

  return (
    <View style={styles.container} testID="splash-screen">
      <ActivityIndicator color={theme.primary} size="large" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.bg, justifyContent: "center", alignItems: "center" },
});
