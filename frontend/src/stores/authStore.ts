import { create } from "zustand";
import { persist } from "zustand/middleware";
// IMPORTANTE: Use o tipo real gerado pelo Orval
import type { UserData } from "@/api/generated/v1/models";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserData | null; // Sincronizado com o Django
  isAuthenticated: boolean;
  // Nomeado como login para o fluxo completo do LoginPage
  login: (access: string, refresh: string, user: UserData) => void;
  logout: () => void;
  // O Axios vai usar isso para apenas trocar os tokens sem mexer no usuário
  updateTokens: (access: string, refresh?: string) => void;
  updateUser: (user: Partial<UserData>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,

      login: (access, refresh, user) =>
        set({
          accessToken: access,
          refreshToken: refresh,
          user,
          isAuthenticated: true,
        }),

      logout: () =>
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
        }),

      updateTokens: (access, refresh) =>
        set((state) => ({
          accessToken: access,
          refreshToken: refresh || state.refreshToken,
        })),

      updateUser: (userData) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        })),
    }),
    {
      name: "wedding-auth-storage", // Nome mais específico para evitar conflitos
    },
  ),
);
