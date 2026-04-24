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
import { useAuth } from "../../src/context/AuthContext";
import { theme } from "../../src/lib/api";
import { Ionicons } from "@expo/vector-icons";
import { PasswordInput } from "../../src/components/PasswordInput";
import { LanguagePicker } from "../../src/components/LanguagePicker";
import { useTranslation } from "react-i18next";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Login() {
  const router = useRouter();
  const { login } = useAuth();
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async () => {
    setError(null);
    if (!email || !password) {
      setError("Inserisci email e password");
      return;
    }
    setLoading(true);
    try {
      await login(email.trim(), password);
      router.replace("/");
    } catch (e: any) {
      setError(e.message || t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: theme.bg }} edges={["top"]}>
      <View style={{ alignItems: "flex-end", paddingHorizontal: 16, paddingTop: 8 }}>
        <LanguagePicker variant="compact" onChange={() => setEmail((e) => e)} />
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
              <Ionicons name="sparkles" size={48} color={theme.primary} />
              <Text style={styles.brand} testID="brand-title">
                Lo Sapevi che?
              </Text>
              <Text style={styles.tagline}>{t("auth.loginTagline")}</Text>
            </View>

            <View style={styles.card}>
              <Text style={styles.label}>{t("common.email")}</Text>
              <TextInput
                testID="login-email"
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
              testID="login-password"
              placeholder="•••••••"
              value={password}
              onChangeText={setPassword}
            />

            {error && (
              <Text style={styles.error} testID="login-error">
                {error}
              </Text>
            )}

            <TouchableOpacity
              testID="login-submit"
              style={styles.btn}
              onPress={onSubmit}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color={theme.bg} />
              ) : (
                <Text style={styles.btnText}>{t("auth.login")}</Text>
              )}
            </TouchableOpacity>

            <Link href="/auth/forgot" asChild>
              <TouchableOpacity testID="go-forgot" style={styles.forgotBtn}>
                <Text style={styles.forgotText}>{t("auth.forgotPassword")}</Text>
              </TouchableOpacity>
            </Link>

            <View style={styles.footer}>
              <Text style={styles.footerText}>{t("auth.noAccount")}</Text>
              <Link href="/auth/register" asChild>
                <TouchableOpacity testID="go-register">
                  <Text style={styles.link}>{t("auth.register")}</Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>
        </ScrollView>
      </TouchableWithoutFeedback>
    </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  scroll: { flexGrow: 1, padding: 24, paddingTop: 60, paddingBottom: 60 },
  logoWrap: { alignItems: "center", marginBottom: 40 },
  brand: {
    fontSize: 36,
    fontWeight: "300",
    color: theme.text,
    marginTop: 12,
    letterSpacing: -0.5,
    fontStyle: "italic",
  },
  tagline: { color: theme.textMuted, marginTop: 8, fontSize: 14 },
  card: {
    backgroundColor: theme.surface,
    borderRadius: 24,
    padding: 24,
    borderWidth: 1,
    borderColor: theme.border,
  },
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
  btn: {
    backgroundColor: theme.primary,
    borderRadius: 999,
    paddingVertical: 16,
    alignItems: "center",
    marginTop: 24,
  },
  btnText: { color: theme.bg, fontWeight: "700", fontSize: 16, letterSpacing: 0.5 },
  forgotBtn: { alignSelf: "center", marginTop: 14, paddingVertical: 6, paddingHorizontal: 10 },
  forgotText: { color: theme.textMuted, fontSize: 14, textDecorationLine: "underline" },
  error: { color: theme.error, marginTop: 12, textAlign: "center" },
  footer: { flexDirection: "row", justifyContent: "center", marginTop: 20, gap: 6 },
  footerText: { color: theme.textMuted },
  link: { color: theme.primary, fontWeight: "600" },
});
