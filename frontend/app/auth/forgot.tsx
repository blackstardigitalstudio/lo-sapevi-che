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
} from "react-native";
import { useRouter, Link } from "expo-router";
import { api, theme } from "../../src/lib/api";
import { Ionicons } from "@expo/vector-icons";
import { PasswordInput } from "../../src/components/PasswordInput";
import { useTranslation } from "react-i18next";

type Step = "email" | "reset" | "done";

export default function Forgot() {
  const router = useRouter();
  const { t } = useTranslation();
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmitEmail = async () => {
    setError(null);
    if (!email.trim()) {
      setError(t("auth.emailEmpty"));
      return;
    }
    setLoading(true);
    try {
      const res = await api.forgotQuestion(email.trim());
      setQuestion(res.security_question);
      setStep("reset");
    } catch (e: any) {
      setError(e.message || t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  const onSubmitReset = async () => {
    setError(null);
    if (!answer.trim()) {
      setError(t("auth.answerEmpty"));
      return;
    }
    if (newPassword.length < 6) {
      setError(t("auth.passwordTooShort"));
      return;
    }
    if (newPassword !== confirmPassword) {
      setError(t("auth.passwordsDontMatch"));
      return;
    }
    setLoading(true);
    try {
      await api.forgotReset({
        email: email.trim(),
        security_answer: answer.trim(),
        new_password: newPassword,
      });
      setStep("done");
    } catch (e: any) {
      setError(e.message || t("common.error"));
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
            <Ionicons name="key" size={44} color={theme.primary} />
            <Text style={styles.brand}>{t("auth.forgotTitle")}</Text>
            <Text style={styles.tagline}>
              {step === "email" && t("auth.forgotStep1Tagline")}
              {step === "reset" && t("auth.forgotStep2Tagline")}
              {step === "done" && t("auth.forgotDoneTagline")}
            </Text>
          </View>

          <View style={styles.card}>
            {step === "email" && (
              <>
                <Text style={styles.label}>{t("common.email")}</Text>
                <TextInput
                  testID="forgot-email"
                  style={styles.input}
                  placeholder={t("auth.emailPlaceholder")}
                  placeholderTextColor={theme.textMuted}
                  autoCapitalize="none"
                  keyboardType="email-address"
                  value={email}
                  onChangeText={setEmail}
                />

                {error && <Text style={styles.error} testID="forgot-error">{error}</Text>}

                <TouchableOpacity
                  testID="forgot-continue"
                  style={styles.btn}
                  onPress={onSubmitEmail}
                  disabled={loading}
                >
                  {loading ? (
                    <ActivityIndicator color={theme.bg} />
                  ) : (
                    <Text style={styles.btnText}>{t("common.continue")}</Text>
                  )}
                </TouchableOpacity>
              </>
            )}

            {step === "reset" && (
              <>
                <View style={styles.questionBox}>
                  <Text style={styles.questionLabel}>{t("auth.yourQuestion")}</Text>
                  <Text style={styles.questionText}>{question}</Text>
                </View>

                <Text style={styles.label}>{t("auth.securityAnswer")}</Text>
                <TextInput
                  testID="forgot-answer"
                  style={styles.input}
                  placeholder={t("auth.securityAnswerPlaceholder")}
                  placeholderTextColor={theme.textMuted}
                  value={answer}
                  onChangeText={setAnswer}
                  autoCapitalize="none"
                />

                <Text style={styles.label}>{t("auth.newPassword")}</Text>
                <PasswordInput
                  testID="forgot-newpassword"
                  placeholder={t("auth.passwordHint")}
                  value={newPassword}
                  onChangeText={setNewPassword}
                />

                <Text style={styles.label}>{t("auth.confirmPassword")}</Text>
                <PasswordInput
                  testID="forgot-confirmpassword"
                  placeholder={t("auth.confirmPasswordPlaceholder")}
                  value={confirmPassword}
                  onChangeText={setConfirmPassword}
                />

                {error && <Text style={styles.error} testID="forgot-error">{error}</Text>}

                <TouchableOpacity
                  testID="forgot-reset-submit"
                  style={styles.btn}
                  onPress={onSubmitReset}
                  disabled={loading}
                >
                  {loading ? (
                    <ActivityIndicator color={theme.bg} />
                  ) : (
                    <Text style={styles.btnText}>{t("auth.resetPassword")}</Text>
                  )}
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.secondaryBtn}
                  onPress={() => {
                    setStep("email");
                    setAnswer("");
                    setNewPassword("");
                    setConfirmPassword("");
                    setError(null);
                  }}
                >
                  <Text style={styles.secondaryText}>{t("auth.changeEmail")}</Text>
                </TouchableOpacity>
              </>
            )}

            {step === "done" && (
              <View style={{ alignItems: "center" }}>
                <Ionicons name="checkmark-circle" size={60} color={theme.success} />
                <Text style={styles.successTitle}>{t("auth.allDone")}</Text>
                <Text style={styles.successText}>{t("auth.allDoneBody")}</Text>
                <TouchableOpacity
                  testID="forgot-go-login"
                  style={[styles.btn, { marginTop: 20 }]}
                  onPress={() => router.replace("/auth/login")}
                >
                  <Text style={styles.btnText}>{t("auth.goToLogin")}</Text>
                </TouchableOpacity>
              </View>
            )}

            {step !== "done" && (
              <View style={styles.footer}>
                <Text style={styles.footerText}>{t("auth.rememberPassword")}</Text>
                <Link href="/auth/login" asChild>
                  <TouchableOpacity testID="go-login">
                    <Text style={styles.link}>{t("auth.login")}</Text>
                  </TouchableOpacity>
                </Link>
              </View>
            )}
          </View>
        </ScrollView>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  scroll: { flexGrow: 1, padding: 24, paddingTop: 60, paddingBottom: 60 },
  logoWrap: { alignItems: "center", marginBottom: 32 },
  brand: { fontSize: 26, fontWeight: "300", color: theme.text, marginTop: 12, fontStyle: "italic" },
  tagline: { color: theme.textMuted, marginTop: 8, fontSize: 14, textAlign: "center", paddingHorizontal: 20 },
  card: { backgroundColor: theme.surface, borderRadius: 24, padding: 24, borderWidth: 1, borderColor: theme.border },
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
  questionBox: {
    backgroundColor: theme.surfaceAlt,
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.border,
    marginBottom: 4,
  },
  questionLabel: { color: theme.primary, fontSize: 11, letterSpacing: 0.8, marginBottom: 4 },
  questionText: { color: theme.text, fontSize: 15, fontWeight: "500" },
  btn: { backgroundColor: theme.primary, borderRadius: 999, paddingVertical: 16, alignItems: "center", marginTop: 24 },
  btnText: { color: theme.bg, fontWeight: "700", fontSize: 16, letterSpacing: 0.5 },
  secondaryBtn: { alignSelf: "center", marginTop: 14, paddingVertical: 6 },
  secondaryText: { color: theme.textMuted, fontSize: 14, textDecorationLine: "underline" },
  error: { color: theme.error, marginTop: 12, textAlign: "center" },
  footer: { flexDirection: "row", justifyContent: "center", marginTop: 22, gap: 6 },
  footerText: { color: theme.textMuted },
  link: { color: theme.primary, fontWeight: "600" },
  successTitle: { color: theme.text, fontSize: 22, fontWeight: "600", marginTop: 14 },
  successText: { color: theme.textMuted, fontSize: 14, textAlign: "center", marginTop: 10, lineHeight: 20 },
});
