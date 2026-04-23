import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import * as Localization from "expo-localization";
import AsyncStorage from "@react-native-async-storage/async-storage";
import it from "./locales/it.json";
import en from "./locales/en.json";
import es from "./locales/es.json";

export const LANG_KEY = "@losapevi_lang";

export type Lang = "it" | "en" | "es";
export const SUPPORTED: Lang[] = ["it", "en", "es"];

export const LANG_META: Record<Lang, { label: string; flag: string; native: string }> = {
  it: { label: "Italiano", native: "Italiano", flag: "🇮🇹" },
  en: { label: "English", native: "English", flag: "🇬🇧" },
  es: { label: "Español", native: "Español", flag: "🇪🇸" },
};

function detectInitialLanguage(): Lang {
  try {
    const locales = Localization.getLocales();
    const code = (locales?.[0]?.languageCode || "it").toLowerCase();
    if ((SUPPORTED as string[]).includes(code)) return code as Lang;
  } catch {}
  return "it";
}

let _initialized = false;

export async function initI18n(): Promise<void> {
  if (_initialized) return;
  let saved: Lang | null = null;
  try {
    const raw = (await AsyncStorage.getItem(LANG_KEY)) as Lang | null;
    if (raw && (SUPPORTED as string[]).includes(raw)) saved = raw;
  } catch {}
  const lng = saved ?? detectInitialLanguage();
  await i18n
    .use(initReactI18next)
    .init({
      compatibilityJSON: "v4",
      resources: {
        it: { translation: it },
        en: { translation: en },
        es: { translation: es },
      },
      lng,
      fallbackLng: "it",
      interpolation: { escapeValue: false },
      returnNull: false,
    });
  _initialized = true;
}

export async function changeLanguage(lang: Lang): Promise<void> {
  await i18n.changeLanguage(lang);
  try {
    await AsyncStorage.setItem(LANG_KEY, lang);
  } catch {}
}

export function currentLanguage(): Lang {
  const lng = (i18n.language || "it").split("-")[0] as Lang;
  return (SUPPORTED as string[]).includes(lng) ? lng : "it";
}

export default i18n;
