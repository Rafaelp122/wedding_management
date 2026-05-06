import { create } from "zustand";
import { persist } from "zustand/middleware";
// IMPORTANTE: Use o tipo real gerado pelo Orval
import type { UserDataOut } from "@/api/generated/v1/models/userDataOut";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserDataOut | null; // Sincronizado com o Django
  isAuthenticated: boolean;
  // Nomeado como login para o fluxo completo do LoginPage
  login: (access: string, refresh: string, user: UserDataOut) => void;
  logout: () => void;
  // O Axios vai usar isso para apenas trocar os tokens sem mexer no usuário
  updateTokens: (access: string, refresh?: string) => void;
  updateUser: (user: Partial<UserDataOut>) => void;
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
      version: 1,
      name: "wedding-auth-storage", // Nome mais específico para evitar conflitos
    },
  ),
);
