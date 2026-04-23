import { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
  Pressable,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useTranslation } from "react-i18next";
import { api, theme } from "../lib/api";
import {
  SUPPORTED,
  LANG_META,
  changeLanguage,
  currentLanguage,
  Lang,
} from "../lib/i18n";

type Variant = "compact" | "row";

type Props = {
  /**
   * - "compact": small globe button (e.g. top-right of auth screens)
   * - "row": full-width row with icon + label + chevron (for Profile page)
   */
  variant?: Variant;
  onChange?: (lang: Lang) => void;
};

export function LanguagePicker({ variant = "compact", onChange }: Props) {
  const { t, i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  const lang = currentLanguage();
  const meta = LANG_META[lang];

  const select = async (l: Lang) => {
    setOpen(false);
    if (l === lang) return;
    await changeLanguage(l);
    // Sync to backend if the user is logged in. Silent fail if not auth'd yet.
    try {
      const token = await api.getToken();
      if (token) await api.setLanguage(l);
    } catch {}
    onChange?.(l);
  };

  return (
    <>
      {variant === "compact" ? (
        <TouchableOpacity
          style={styles.compactBtn}
          onPress={() => setOpen(true)}
          testID="lang-picker-compact"
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <Text style={styles.flag}>{meta.flag}</Text>
          <Text style={styles.compactCode}>{lang.toUpperCase()}</Text>
          <Ionicons name="chevron-down" size={14} color={theme.text} />
        </TouchableOpacity>
      ) : (
        <TouchableOpacity
          style={styles.rowBtn}
          onPress={() => setOpen(true)}
          testID="lang-picker-row"
        >
          <Ionicons name="language-outline" size={20} color={theme.text} />
          <Text style={styles.rowText}>{t("profile.language")}</Text>
          <Text style={styles.rowValue}>
            {meta.flag}  {meta.native}
          </Text>
          <Ionicons name="chevron-forward" size={18} color={theme.textMuted} />
        </TouchableOpacity>
      )}

      <Modal
        transparent
        visible={open}
        animationType="fade"
        onRequestClose={() => setOpen(false)}
      >
        <Pressable style={styles.backdrop} onPress={() => setOpen(false)}>
          <Pressable style={styles.card} onPress={() => {}}>
            <Text style={styles.title}>{t("language.chooseLanguage")}</Text>
            {SUPPORTED.map((l) => {
              const m = LANG_META[l];
              const active = l === lang;
              return (
                <TouchableOpacity
                  key={l}
                  style={[styles.option, active && styles.optionActive]}
                  onPress={() => select(l)}
                  testID={`lang-option-${l}`}
                >
                  <Text style={styles.optFlag}>{m.flag}</Text>
                  <Text style={styles.optLabel}>{m.native}</Text>
                  {active && (
                    <Ionicons name="checkmark" size={18} color={theme.primary} />
                  )}
                </TouchableOpacity>
              );
            })}
          </Pressable>
        </Pressable>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  compactBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    backgroundColor: theme.surface,
    borderWidth: 1,
    borderColor: theme.border,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 999,
  },
  flag: { fontSize: 16 },
  compactCode: { color: theme.text, fontWeight: "600", fontSize: 13, letterSpacing: 0.5 },
  rowBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    paddingVertical: 14,
    paddingHorizontal: 14,
    backgroundColor: theme.surface,
    borderRadius: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: theme.border,
  },
  rowText: { color: theme.text, fontSize: 15, flex: 1 },
  rowValue: { color: theme.textMuted, fontSize: 14 },
  backdrop: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.7)",
    justifyContent: "center",
    padding: 24,
  },
  card: {
    backgroundColor: theme.surface,
    borderRadius: 20,
    padding: 20,
    borderWidth: 1,
    borderColor: theme.border,
  },
  title: { color: theme.text, fontSize: 18, fontWeight: "600", marginBottom: 14 },
  option: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    paddingVertical: 14,
    paddingHorizontal: 12,
    borderRadius: 10,
    marginBottom: 4,
  },
  optionActive: { backgroundColor: theme.surfaceAlt },
  optFlag: { fontSize: 22 },
  optLabel: { color: theme.text, fontSize: 15, flex: 1 },
});
