import React from "react";
import { Modal, View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useTranslation } from "react-i18next";
import { theme } from "../lib/api";

export type Trophy = {
  id: string;
  name: string;
  desc: string;
  icon: string;
};

export function TrophyModal({
  trophies,
  onClose,
}: {
  trophies: Trophy[];
  onClose: () => void;
}) {
  const { t } = useTranslation();
  const visible = trophies.length > 0;
  const first = trophies[0];

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <View style={styles.card} testID="trophy-modal">
          <View style={styles.iconWrap}>
            <Ionicons name={(first?.icon || "trophy") as any} size={42} color={theme.bg} />
          </View>
          <Text style={styles.kicker}>{t("trophy.unlocked")}</Text>
          <Text style={styles.title}>{first?.name}</Text>
          <Text style={styles.desc}>{first?.desc}</Text>
          {trophies.length > 1 && (
            <Text style={styles.more}>{t("trophy.more", { n: trophies.length - 1 })}</Text>
          )}
          <TouchableOpacity style={styles.btn} onPress={onClose} testID="trophy-modal-close">
            <Text style={styles.btnText}>{t("common.continue")}</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.85)", alignItems: "center", justifyContent: "center", padding: 32 },
  card: {
    width: "100%",
    backgroundColor: theme.surface,
    borderRadius: 24,
    padding: 28,
    alignItems: "center",
    borderWidth: 1,
    borderColor: theme.primary,
  },
  iconWrap: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: theme.primary,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 18,
  },
  kicker: { color: theme.primary, fontSize: 11, letterSpacing: 2, fontWeight: "700", marginBottom: 8 },
  title: { color: theme.text, fontSize: 26, fontWeight: "300", fontStyle: "italic", marginBottom: 8, textAlign: "center" },
  desc: { color: theme.textMuted, fontSize: 14, textAlign: "center", lineHeight: 20 },
  more: { color: theme.primary, fontSize: 12, marginTop: 10, fontStyle: "italic" },
  btn: { backgroundColor: theme.primary, paddingHorizontal: 32, paddingVertical: 14, borderRadius: 999, marginTop: 24 },
  btnText: { color: theme.bg, fontWeight: "700", fontSize: 15, letterSpacing: 0.3 },
});
