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
import { PasswordInput } from "../../src/components/PasswordInput";
import { LanguagePicker } from "../../src/components/LanguagePicker";
import { useTranslation } from "react-i18next";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Register() {
  const router = useRouter();
  const { register } = useAuth();
  const { t } = useTranslation();
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
      setError(t("common.required"));
      return;
    }
    if (password.length < 6) {
      setError(t("auth.passwordTooShort"));
      return;
    }
    if (!finalQuestion || finalQuestion.length < 3) {
      setError(t("auth.questionMissing"));
      return;
    }
    if (!securityAnswer.trim()) {
      setError(t("auth.answerMissing"));
      return;
    }
    setLoading(true);
    try {
      await register(
        email.trim(),
        password,
        name.trim(),
        [],
        finalQuestion,
        securityAnswer.trim(),
      );
      router.replace("/onboarding");
    } catch (e: any) {
      setError(e.message || "Errore");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: theme.bg }} edges={["top"]}>
      <View style={{ alignItems: "flex-end", paddingHorizontal: 16, paddingTop: 8 }}>
        <LanguagePicker variant="compact" onChange={() => setName((n) => n)} />
      </View>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
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
              <Text style={styles.brand}>{t("auth.registerTitle")}</Text>
              <Text style={styles.tagline}>{t("auth.registerTagline")}</Text>
            </View>

            <View style={styles.card}>
              <Text style={styles.label}>{t("common.name")}</Text>
              <TextInput
                testID="register-name"
                style={styles.input}
                placeholder={t("auth.namePlaceholder")}
                placeholderTextColor={theme.textMuted}
                value={name}
                onChangeText={setName}
              />

              <Text style={styles.label}>{t("common.email")}</Text>
              <TextInput
                testID="register-email"
                style={styles.input}
                placeholder={t("auth.emailPlaceholder")}
                placeholderTextColor={theme.textMuted}
                autoCapitalize="none"
                keyboardType="email-address"
                value={email}
                onChangeText={setEmail}
              />

              <Text style={styles.label}>{t("common.password")}</Text>
              <PasswordInput
                testID="register-password"
                placeholder={t("auth.passwordHint")}
                value={password}
                onChangeText={setPassword}
              />

              <View style={styles.sectionDivider} />
              <View style={styles.securityHint}>
                <Ionicons name="shield-checkmark" size={16} color={theme.primary} />
                <Text style={styles.hintText}>{t("auth.securityHint")}</Text>
              </View>

              <Text style={styles.label}>{t("auth.securityQuestion")}</Text>
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
                  {isCustom ? t("auth.customQuestion") : selectedQuestion}
                </Text>
                <Ionicons name="chevron-down" size={18} color={theme.textMuted} />
              </TouchableOpacity>

              {isCustom && (
                <TextInput
                  testID="register-question-custom"
                  style={[styles.input, { marginTop: 10 }]}
                  placeholder={t("auth.customQuestionPlaceholder")}
                  placeholderTextColor={theme.textMuted}
                  value={customQuestion}
                  onChangeText={setCustomQuestion}
                  maxLength={200}
                />
              )}

              <Text style={styles.label}>{t("auth.securityAnswer")}</Text>
              <TextInput
                testID="register-answer"
                style={styles.input}
                placeholder={t("auth.securityAnswerPlaceholder")}
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
                  <Text style={styles.btnText}>{t("auth.createAccount")}</Text>
                )}
              </TouchableOpacity>

              <View style={styles.footer}>
                <Text style={styles.footerText}>{t("auth.hasAccount")}</Text>
                <Link href="/auth/login" asChild>
                  <TouchableOpacity testID="go-login">
                    <Text style={styles.link}>{t("auth.login")}</Text>
                  </TouchableOpacity>
                </Link>
              </View>
            </View>
          </ScrollView>
        </TouchableWithoutFeedback>

        <Modal transparent visible={pickerOpen} animationType="fade" onRequestClose={() => setPickerOpen(false)}>
          <Pressable style={styles.modalBackdrop} onPress={() => setPickerOpen(false)}>
            <Pressable style={styles.modalCard} onPress={() => {}}>
              <Text style={styles.modalTitle}>{t("auth.chooseQuestion")}</Text>
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
                    ✏️  {t("auth.customQuestion")}
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
  sectionDivider: { height: 1, backgroundColor: theme.border, marginTop: 20, marginBottom: 4 },
  securityHint: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: 10, marginBottom: 2 },
  hintText: { color: theme.textMuted, fontSize: 12, flex: 1 },
  btn: { backgroundColor: theme.primary, borderRadius: 999, paddingVertical: 16, alignItems: "center", marginTop: 24 },
  btnText: { color: theme.bg, fontWeight: "700", fontSize: 16, letterSpacing: 0.5 },
  error: { color: theme.error, marginTop: 12, textAlign: "center" },
  footer: { flexDirection: "row", justifyContent: "center", marginTop: 20, gap: 6 },
  footerText: { color: theme.textMuted },
  link: { color: theme.primary, fontWeight: "600" },
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
