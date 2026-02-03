"use client";

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { authApi } from "@/api/auth";
import type { User } from "@/types/auth.types";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isInitialized: boolean;
  setAuth: (user: User, accessToken: string, refreshToken?: string) => void;
  logout: () => void;
  initializeAuth: () => Promise<void>;
  validateSession: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isInitialized: false,
      setAuth: (user, accessToken, refreshToken) => {
        set({
          user,
          accessToken,
          refreshToken: refreshToken || null,
          isAuthenticated: true,
          isInitialized: true,
        });
      },
      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isInitialized: true,
        });
      },
      initializeAuth: async () => {
        const { accessToken } = get();

        if (!accessToken) {
          set({ isInitialized: true });
          return;
        }

        try {
          const user = await authApi.getCurrentUser(accessToken);

          set({
            user,
            accessToken,
            isAuthenticated: true,
            isInitialized: true,
          });
        } catch (error) {
          get().logout();
        }
      },
      validateSession: async () => {
        const { accessToken } = get();

        if (!accessToken) {
          return false;
        }

        try {
          const user = await authApi.getCurrentUser(accessToken);

          set({
            user,
            isAuthenticated: true,
          });

          return true;
        } catch (error) {
          get().logout();
          return false;
        }
      },
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        if (state) {
          if (!state.isInitialized) {
            state.initializeAuth();
          }
        }
      },
    },
  ),
);
