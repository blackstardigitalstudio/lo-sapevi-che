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
  Modal,
  Pressable,
  Alert,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import { api, theme } from "../src/lib/api";
import { useAuth } from "../src/context/AuthContext";
import { Ionicons } from "@expo/vector-icons";
import { SECURITY_QUESTIONS, CUSTOM_QUESTION_VALUE } from "../src/lib/securityQuestions";
import { PasswordInput } from "../src/components/PasswordInput";

export default function SecurityScreen() {
  const router = useRouter();
  const { user, refresh } = useAuth();
  const [selectedQuestion, setSelectedQuestion] = useState<string>(SECURITY_QUESTIONS[0]);
  const [customQuestion, setCustomQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [pickerOpen, setPickerOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isCustom = selectedQuestion === CUSTOM_QUESTION_VALUE;
  const finalQuestion = isCustom ? customQuestion.trim() : selectedQuestion;

  const onSubmit = async () => {
    setError(null);
    if (!finalQuestion || finalQuestion.length < 3) {
      setError("Scegli o scrivi una domanda di sicurezza");
      return;
    }
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
        security_question: finalQuestion,
        security_answer: answer.trim(),
        current_password: currentPassword,
      });
      await refresh();
      Alert.alert(
        "Fatto!",
        "La tua domanda di sicurezza è stata salvata. Ora potrai recuperare la password in qualsiasi momento.",
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
                  ? "Aggiorna la tua domanda"
                  : "Imposta la domanda di sicurezza"}
              </Text>
              <Text style={styles.heroText}>
                Serve a recuperare la password se la dimentichi. La risposta viene salvata in modo sicuro.
              </Text>
            </View>

            <View style={styles.card}>
              <Text style={styles.label}>Domanda</Text>
              <TouchableOpacity
                style={styles.select}
                onPress={() => setPickerOpen(true)}
                testID="security-question-picker"
              >
                <Text style={[styles.selectText, { color: theme.text }]} numberOfLines={2}>
                  {isCustom ? "Scrivi una domanda personalizzata" : selectedQuestion}
                </Text>
                <Ionicons name="chevron-down" size={18} color={theme.textMuted} />
              </TouchableOpacity>

              {isCustom && (
                <TextInput
                  testID="security-question-custom"
                  style={[styles.input, { marginTop: 10 }]}
                  placeholder="La tua domanda personalizzata"
                  placeholderTextColor={theme.textMuted}
                  value={customQuestion}
                  onChangeText={setCustomQuestion}
                  maxLength={200}
                />
              )}

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
              <PasswordInput
                testID="security-current-password"
                placeholder="Per confermare che sei tu"
                value={currentPassword}
                onChangeText={setCurrentPassword}
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

        <Modal transparent visible={pickerOpen} animationType="fade" onRequestClose={() => setPickerOpen(false)}>
          <Pressable style={styles.modalBackdrop} onPress={() => setPickerOpen(false)}>
            <Pressable style={styles.modalCard} onPress={() => {}}>
              <Text style={styles.modalTitle}>Scegli una domanda</Text>
              <ScrollView style={{ maxHeight: 400 }}>
                {SECURITY_QUESTIONS.map((q) => (
                  <TouchableOpacity
                    key={q}
                    style={[styles.optionRow, selectedQuestion === q && styles.optionRowActive]}
                    onPress={() => {
                      setSelectedQuestion(q);
                      setPickerOpen(false);
                    }}
                  >
                    <Text style={styles.optionText}>{q}</Text>
                    {selectedQuestion === q && (
                      <Ionicons name="checkmark" size={18} color={theme.primary} />
                    )}
                  </TouchableOpacity>
                ))}
                <TouchableOpacity
                  style={[styles.optionRow, isCustom && styles.optionRowActive]}
                  onPress={() => {
                    setSelectedQuestion(CUSTOM_QUESTION_VALUE);
                    setPickerOpen(false);
                  }}
                >
                  <Text style={[styles.optionText, { fontStyle: "italic" }]}>
                    ✏️  Scrivi una domanda personalizzata
                  </Text>
                  {isCustom && <Ionicons name="checkmark" size={18} color={theme.primary} />}
                </TouchableOpacity>
              </ScrollView>
            </Pressable>
          </Pressable>
        </Modal>
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
  label: { color: theme.textMuted, fontSize: 12, letterSpacing: 0.5, marginBottom: 6, marginTop: 12, textTransform: "uppercase" },
  input: {
    backgroundColor: theme.bg,
    borderWidth: 1,
    borderColor: theme.border,
    borderRadius: 12,
    padding: 14,
    color: theme.text,
    fontSize: 16,
  },
  select: {
    backgroundColor: theme.bg,
    borderWidth: 1,
    borderColor: theme.border,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 14,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    minHeight: 50,
  },
  selectText: { flex: 1, fontSize: 15, marginRight: 10 },
  btn: { backgroundColor: theme.primary, borderRadius: 999, paddingVertical: 16, alignItems: "center", marginTop: 20 },
  btnText: { color: theme.bg, fontWeight: "700", fontSize: 16, letterSpacing: 0.5 },
  error: { color: theme.error, marginTop: 12, textAlign: "center" },
  modalBackdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.7)", justifyContent: "center", padding: 24 },
  modalCard: { backgroundColor: theme.surface, borderRadius: 20, padding: 20, borderWidth: 1, borderColor: theme.border },
  modalTitle: { color: theme.text, fontSize: 18, fontWeight: "600", marginBottom: 12 },
  optionRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 14,
    paddingHorizontal: 12,
    borderRadius: 10,
    marginBottom: 4,
  },
  optionRowActive: { backgroundColor: theme.surfaceAlt },
  optionText: { color: theme.text, fontSize: 15, flex: 1, marginRight: 8 },
});
