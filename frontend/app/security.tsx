import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator,
  Keyboard,
  TouchableWithoutFeedback,
  Alert,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { api, theme } from "../src/lib/api";
import { useAuth } from "../src/context/AuthContext";
import { Ionicons } from "@expo/vector-icons";
import { SECURITY_QUESTION } from "../src/lib/securityQuestions";

export default function SecurityScreen() {
  const router = useRouter();
  const { user, refresh } = useAuth();
  const [answer, setAnswer] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async () => {
    setError(null);
    if (!answer.trim()) {
      setError("Inserisci la risposta");
      return;
    }
    if (!currentPassword) {
      setError("Inserisci la tua password attuale per confermare");
      return;
    }
    setLoading(true);
    try {
      await api.setSecurityQuestion({
        security_question: SECURITY_QUESTION,
        security_answer: answer.trim(),
        current_password: currentPassword,
      });
      await refresh();
      Alert.alert(
        "Fatto!",
        "La tua risposta di sicurezza è stata salvata. Ora potrai recuperare la password in qualsiasi momento.",
        [{ text: "OK", onPress: () => router.back() }],
      );
    } catch (e: any) {
      setError(e.message || "Errore");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: theme.bg }} edges={["top"]}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : "height"}
      >
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backBtn} testID="security-back">
            <Ionicons name="chevron-back" size={26} color={theme.text} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Sicurezza</Text>
          <View style={{ width: 32 }} />
        </View>

        <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
          <ScrollView
            contentContainerStyle={styles.scroll}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={false}
          >
            <View style={styles.heroCard}>
              <Ionicons name="shield-checkmark" size={32} color={theme.primary} />
              <Text style={styles.heroTitle}>
                {user?.has_security_question
                  ? "Aggiorna la tua risposta"
                  : "Imposta la risposta di sicurezza"}
              </Text>
              <Text style={styles.heroText}>
                Serve a recuperare la password se la dimentichi. La risposta viene salvata in modo sicuro.
              </Text>
            </View>

            <View style={styles.card}>
              <View style={styles.questionBox}>
                <Text style={styles.questionLabel}>DOMANDA DI SICUREZZA</Text>
                <Text style={styles.questionText}>{SECURITY_QUESTION}</Text>
              </View>

              <Text style={styles.label}>Risposta</Text>
              <TextInput
                testID="security-answer"
                style={styles.input}
                placeholder="La tua risposta segreta"
                placeholderTextColor={theme.textMuted}
                value={answer}
                onChangeText={setAnswer}
                autoCapitalize="none"
                maxLength={200}
              />

              <Text style={styles.label}>Password attuale</Text>
              <TextInput
                testID="security-current-password"
                style={styles.input}
                placeholder="Per confermare che sei tu"
                placeholderTextColor={theme.textMuted}
                value={currentPassword}
                onChangeText={setCurrentPassword}
                secureTextEntry
              />

              {error && <Text style={styles.error} testID="security-error">{error}</Text>}

              <TouchableOpacity
                testID="security-submit"
                style={styles.btn}
                onPress={onSubmit}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator color={theme.bg} />
                ) : (
                  <Text style={styles.btnText}>Salva</Text>
                )}
              </TouchableOpacity>
            </View>
          </ScrollView>
        </TouchableWithoutFeedback>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: theme.border,
  },
  backBtn: { padding: 6 },
  headerTitle: { color: theme.text, fontSize: 18, fontWeight: "600" },
  scroll: { padding: 20, paddingBottom: 40 },
  heroCard: {
    backgroundColor: theme.surface,
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: theme.border,
    alignItems: "center",
    marginBottom: 16,
  },
  heroTitle: { color: theme.text, fontSize: 18, fontWeight: "600", marginTop: 10, textAlign: "center" },
  heroText: { color: theme.textMuted, fontSize: 13, marginTop: 8, textAlign: "center", lineHeight: 18 },
  card: {
    backgroundColor: theme.surface,
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: theme.border,
  },
  questionBox: {
    backgroundColor: theme.surfaceAlt,
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.border,
  },
  questionLabel: { color: theme.primary, fontSize: 11, letterSpacing: 0.8, marginBottom: 4 },
  questionText: { color: theme.text, fontSize: 15, fontWeight: "500" },
  label: { color: theme.textMuted, fontSize: 12, letterSpacing: 0.5, marginBottom: 6, marginTop: 14, textTransform: "uppercase" },
  input: {
    backgroundColor: theme.bg,
    borderWidth: 1,
    borderColor: theme.border,
    borderRadius: 12,
    padding: 14,
    color: theme.text,
    fontSize: 16,
  },
  btn: { backgroundColor: theme.primary, borderRadius: 999, paddingVertical: 16, alignItems: "center", marginTop: 20 },
  btnText: { color: theme.bg, fontWeight: "700", fontSize: 16, letterSpacing: 0.5 },
  error: { color: theme.error, marginTop: 12, textAlign: "center" },
});
