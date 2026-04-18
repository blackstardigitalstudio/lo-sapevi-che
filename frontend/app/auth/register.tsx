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

export default function Register() {
  const router = useRouter();
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    setLoading(true);
    try {
      await register(email.trim(), password, name.trim(), []);
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
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
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
  btn: { backgroundColor: theme.primary, borderRadius: 999, paddingVertical: 16, alignItems: "center", marginTop: 24 },
  btnText: { color: theme.bg, fontWeight: "700", fontSize: 16, letterSpacing: 0.5 },
  error: { color: theme.error, marginTop: 12, textAlign: "center" },
  footer: { flexDirection: "row", justifyContent: "center", marginTop: 20, gap: 6 },
  footerText: { color: theme.textMuted },
  link: { color: theme.primary, fontWeight: "600" },
});
