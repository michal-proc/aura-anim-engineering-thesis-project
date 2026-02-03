"use client";

import type React from "react";
import { createContext, useContext, useState, useEffect } from "react";

type Locale = "en" | "pl";

interface I18nContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

let translationsCache: Record<Locale, any> | null = null;

async function loadTranslations(): Promise<Record<Locale, any>> {
  if (translationsCache) return translationsCache;

  const [enData, plData] = await Promise.all([
    fetch("/locales/en.json").then((res) => res.json()),
    fetch("/locales/pl.json").then((res) => res.json()),
  ]);

  translationsCache = {
    en: enData,
    pl: plData,
  };

  return translationsCache;
}

function getNestedValue(obj: any, path: string): string | undefined {
  const keys = path.split(".");
  let result = obj;

  for (const key of keys) {
    if (result && typeof result === "object" && key in result) {
      result = result[key];
    } else {
      return undefined;
    }
  }

  return typeof result === "string" ? result : undefined;
}

function detectBrowserLanguage(): Locale {
  if (typeof window === "undefined") return "en";

  const browserLang = navigator.language.toLowerCase();

  // Check if browser language starts with 'pl' (e.g., 'pl', 'pl-PL')
  if (browserLang.startsWith("pl")) {
    return "pl";
  }

  // Default to English
  return "en";
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");
  const [translations, setTranslations] = useState<Record<Locale, any>>({
    en: {},
    pl: {},
  });

  useEffect(() => {
    loadTranslations().then(setTranslations);
  }, []);

  useEffect(() => {
    const savedLocale = localStorage.getItem("locale") as Locale;
    if (savedLocale && (savedLocale === "en" || savedLocale === "pl")) {
      setLocaleState(savedLocale);
    } else {
      const detectedLocale = detectBrowserLanguage();
      setLocaleState(detectedLocale);
      localStorage.setItem("locale", detectedLocale);
    }
  }, []);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    localStorage.setItem("locale", newLocale);
  };

  const t = (key: string): string => {
    const translation = getNestedValue(translations[locale], key);
    return translation || key;
  };

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used within I18nProvider");
  }
  return context;
}

export const useTranslations = useI18n;
