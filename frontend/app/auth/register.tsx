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
} from "react-native";
import { useRouter, Link } from "expo-router";
import { useAuth } from "../../src/context/AuthContext";
import { theme } from "../../src/lib/api";
import { Ionicons } from "@expo/vector-icons";
import { SECURITY_QUESTIONS, CUSTOM_QUESTION_VALUE } from "../../src/lib/securityQuestions";

export default function Register() {
  const router = useRouter();
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [selectedQuestion, setSelectedQuestion] = useState<string>(SECURITY_QUESTIONS[0]);
  const [customQuestion, setCustomQuestion] = useState("");
  const [securityAnswer, setSecurityAnswer] = useState("");
  const [pickerOpen, setPickerOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isCustom = selectedQuestion === CUSTOM_QUESTION_VALUE;
  const finalQuestion = isCustom ? customQuestion.trim() : selectedQuestion;

  const onSubmit = async () => {
    setError(null);
    if (!name || !email || !password) {
      setError("Compila tutti i campi");
      return;
    }
    if (password.length < 6) {
      setError("Password: minimo 6 caratteri");
      return;
    }
    if (!finalQuestion || finalQuestion.length < 3) {
      setError("Scegli o scrivi una domanda di sicurezza");
      return;
    }
    if (!securityAnswer.trim()) {
      setError("Inserisci la risposta alla domanda di sicurezza");
      return;
    }
    setLoading(true);
    try {
      await register(email.trim(), password, name.trim(), [], finalQuestion, securityAnswer.trim());
      router.replace("/onboarding");
    } catch (e: any) {
      setError(e.message || "Errore");
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: theme.bg }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={0}
    >
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <ScrollView
          contentContainerStyle={styles.scroll}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.logoWrap}>
            <Ionicons name="sparkles" size={44} color={theme.primary} />
            <Text style={styles.brand}>Crea il tuo account</Text>
            <Text style={styles.tagline}>Inizia il tuo viaggio nella conoscenza</Text>
          </View>

          <View style={styles.card}>
            <Text style={styles.label}>Nome</Text>
            <TextInput
              testID="register-name"
              style={styles.input}
              placeholder="Come ti chiami?"
              placeholderTextColor={theme.textMuted}
              value={name}
              onChangeText={setName}
            />

            <Text style={styles.label}>Email</Text>
            <TextInput
              testID="register-email"
              style={styles.input}
              placeholder="tu@email.com"
              placeholderTextColor={theme.textMuted}
              autoCapitalize="none"
              keyboardType="email-address"
              value={email}
              onChangeText={setEmail}
            />

            <Text style={styles.label}>Password</Text>
            <TextInput
              testID="register-password"
              style={styles.input}
              placeholder="Minimo 6 caratteri"
              placeholderTextColor={theme.textMuted}
              secureTextEntry
              value={password}
              onChangeText={setPassword}
            />

            <View style={styles.sectionDivider} />
            <View style={styles.securityHint}>
              <Ionicons name="shield-checkmark" size={16} color={theme.primary} />
              <Text style={styles.hintText}>
                Serve per recuperare la password se la dimentichi.
              </Text>
            </View>

            <Text style={styles.label}>Domanda di sicurezza</Text>
            <TouchableOpacity
              testID="register-question-picker"
              style={styles.select}
              onPress={() => setPickerOpen(true)}
            >
              <Text
                style={[
                  styles.selectText,
                  { color: selectedQuestion ? theme.text : theme.textMuted },
                ]}
                numberOfLines={2}
              >
                {isCustom ? "Scrivi una domanda personalizzata" : selectedQuestion}
              </Text>
              <Ionicons name="chevron-down" size={18} color={theme.textMuted} />
            </TouchableOpacity>

            {isCustom && (
              <TextInput
                testID="register-question-custom"
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
              testID="register-answer"
              style={styles.input}
              placeholder="La tua risposta segreta"
              placeholderTextColor={theme.textMuted}
              value={securityAnswer}
              onChangeText={setSecurityAnswer}
              autoCapitalize="none"
              maxLength={200}
            />

            {error && (
              <Text style={styles.error} testID="register-error">
                {error}
              </Text>
            )}

            <TouchableOpacity
              testID="register-submit"
              style={styles.btn}
              onPress={onSubmit}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color={theme.bg} />
              ) : (
                <Text style={styles.btnText}>Crea account</Text>
              )}
            </TouchableOpacity>

            <View style={styles.footer}>
              <Text style={styles.footerText}>Hai già un account?</Text>
              <Link href="/auth/login" asChild>
                <TouchableOpacity testID="go-login">
                  <Text style={styles.link}>Accedi</Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>
        </ScrollView>
      </TouchableWithoutFeedback>

      {/* Question Picker Modal */}
      <Modal transparent visible={pickerOpen} animationType="fade" onRequestClose={() => setPickerOpen(false)}>
        <Pressable style={styles.modalBackdrop} onPress={() => setPickerOpen(false)}>
          <Pressable style={styles.modalCard} onPress={() => {}}>
            <Text style={styles.modalTitle}>Scegli una domanda</Text>
            <ScrollView style={{ maxHeight: 400 }}>
              {SECURITY_QUESTIONS.map((q) => (
                <TouchableOpacity
                  key={q}
                  style={[
                    styles.optionRow,
                    selectedQuestion === q && styles.optionRowActive,
                  ]}
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
                style={[
                  styles.optionRow,
                  isCustom && styles.optionRowActive,
                ]}
                onPress={() => {
                  setSelectedQuestion(CUSTOM_QUESTION_VALUE);
                  setPickerOpen(false);
                }}
              >
                <Text style={[styles.optionText, { fontStyle: "italic" }]}>
                  ✏️  Domanda personalizzata
                </Text>
                {isCustom && <Ionicons name="checkmark" size={18} color={theme.primary} />}
              </TouchableOpacity>
            </ScrollView>
          </Pressable>
        </Pressable>
      </Modal>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  scroll: { flexGrow: 1, padding: 24, justifyContent: "center", minHeight: "100%" },
  logoWrap: { alignItems: "center", marginBottom: 32 },
  brand: { fontSize: 28, fontWeight: "300", color: theme.text, marginTop: 12, fontStyle: "italic" },
  tagline: { color: theme.textMuted, marginTop: 6, fontSize: 14 },
  card: { backgroundColor: theme.surface, borderRadius: 24, padding: 24, borderWidth: 1, borderColor: theme.border },
  label: { color: theme.textMuted, fontSize: 12, letterSpacing: 0.5, marginBottom: 6, marginTop: 10, textTransform: "uppercase" },
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
  sectionDivider: {
    height: 1,
    backgroundColor: theme.border,
    marginTop: 20,
    marginBottom: 4,
  },
  securityHint: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginTop: 10,
    marginBottom: 2,
  },
  hintText: { color: theme.textMuted, fontSize: 12, flex: 1 },
  btn: { backgroundColor: theme.primary, borderRadius: 999, paddingVertical: 16, alignItems: "center", marginTop: 24 },
  btnText: { color: theme.bg, fontWeight: "700", fontSize: 16, letterSpacing: 0.5 },
  error: { color: theme.error, marginTop: 12, textAlign: "center" },
  footer: { flexDirection: "row", justifyContent: "center", marginTop: 20, gap: 6 },
  footerText: { color: theme.textMuted },
  link: { color: theme.primary, fontWeight: "600" },
  modalBackdrop: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.7)",
    justifyContent: "center",
    padding: 24,
  },
  modalCard: {
    backgroundColor: theme.surface,
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: theme.border,
  },
  modalTitle: {
    color: theme.text,
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 12,
  },
  optionRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 14,
    paddingHorizontal: 12,
    borderRadius: 10,
    marginBottom: 4,
  },
  optionRowActive: {
    backgroundColor: theme.surfaceAlt,
  },
  optionText: { color: theme.text, fontSize: 15, flex: 1, marginRight: 8 },
});
