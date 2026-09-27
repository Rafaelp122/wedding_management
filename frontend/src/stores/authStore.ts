import { create } from "zustand";
import { persist } from "zustand/middleware";
import { AXIOS_INSTANCE } from "@/api/axios-instance";
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
    (set, get) => ({
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

      logout: () => {
        const refresh = get().refreshToken;
        if (refresh) {
          // Invalida o refresh token no servidor (RFC 7009)
          AXIOS_INSTANCE.post("/api/v1/auth/logout/", { refresh }).catch(() => {
            // Ignora erros de rede no logout para garantir limpeza de sessão local
          });
        }
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
        });
      },

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
      name: "wedding-auth-storage",
    },
  ),
);
