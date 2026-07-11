"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  ACCENT_PRESETS,
  DEFAULT_ACCENT,
  type AccentName,
} from "./accent";

interface AccentContextValue {
  accent: AccentName;
  setAccent: (next: AccentName) => void;
}

const AccentContext = createContext<AccentContextValue | null>(null);

const STORAGE_KEY = "openradar.web.accent";

/**
 * AccentProvider — applies the chosen preset as `data-accent` on <html>.
 * Persists to localStorage. SSR-safe: initial render uses DEFAULT_ACCENT,
 * then a useEffect hydrates from storage and re-applies.
 */
export function AccentProvider({ children }: { children: ReactNode }) {
  const [accent, setAccentState] = useState<AccentName>(DEFAULT_ACCENT);

  // Hydrate from storage once on mount.
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const saved = window.localStorage.getItem(STORAGE_KEY);
      if (saved && ACCENT_PRESETS.some((p) => p.name === saved)) {
        setAccentState(saved as AccentName);
      }
    } catch {
      // localStorage may be unavailable (private mode, etc.) — ignore.
    }
  }, []);

  // Apply accent attribute to <html> on every change.
  useEffect(() => {
    if (typeof document === "undefined") return;
    document.documentElement.setAttribute("data-accent", accent);
  }, [accent]);

  const setAccent = useCallback((next: AccentName) => {
    setAccentState(next);
    if (typeof window !== "undefined") {
      try {
        window.localStorage.setItem(STORAGE_KEY, next);
      } catch {
        // ignore
      }
    }
  }, []);

  const value = useMemo(() => ({ accent, setAccent }), [accent, setAccent]);

  return (
    <AccentContext.Provider value={value}>{children}</AccentContext.Provider>
  );
}

export function useAccent(): AccentContextValue {
  const ctx = useContext(AccentContext);
  if (!ctx) {
    // Provider missing — fall back to a noop so the page still renders.
    // This should not happen in normal flows; log once for debugging.
    if (typeof console !== "undefined") {
      console.warn("useAccent called outside AccentProvider");
    }
    return { accent: DEFAULT_ACCENT, setAccent: () => {} };
  }
  return ctx;
}