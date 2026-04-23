import { useState } from "react";
import {
  View,
  TextInput,
  TextInputProps,
  TouchableOpacity,
  StyleSheet,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { theme } from "../lib/api";

type Props = Omit<TextInputProps, "secureTextEntry"> & {
  testID?: string;
};

/**
 * Password TextInput with built-in show/hide toggle (eye icon).
 * Drop-in replacement for any TextInput that needed secureTextEntry.
 */
export function PasswordInput({ style, testID, ...props }: Props) {
  const [visible, setVisible] = useState(false);

  return (
    <View style={styles.wrapper}>
      <TextInput
        {...props}
        testID={testID}
        secureTextEntry={!visible}
        autoCapitalize="none"
        autoCorrect={false}
        style={[styles.input, style]}
        placeholderTextColor={theme.textMuted}
      />
      <TouchableOpacity
        onPress={() => setVisible((v) => !v)}
        style={styles.eye}
        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        testID={testID ? `${testID}-toggle` : "password-toggle"}
      >
        <Ionicons
          name={visible ? "eye-off-outline" : "eye-outline"}
          size={22}
          color={theme.textMuted}
        />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    position: "relative",
    justifyContent: "center",
  },
  input: {
    backgroundColor: theme.bg,
    borderWidth: 1,
    borderColor: theme.border,
    borderRadius: 12,
    paddingVertical: 14,
    paddingLeft: 14,
    paddingRight: 46, // space for the eye icon
    color: theme.text,
    fontSize: 16,
  },
  eye: {
    position: "absolute",
    right: 10,
    top: 0,
    bottom: 0,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 6,
  },
});
