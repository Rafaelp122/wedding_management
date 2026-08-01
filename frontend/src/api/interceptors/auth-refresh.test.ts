import { beforeEach, describe, expect, it, vi } from "vitest";
import Axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from "axios";
import { addAuthRefreshInterceptor } from "@/api/interceptors/auth-refresh";
import { useAuthStore } from "@/stores/authStore";

function createMockInstance() {
  const handlers = {
    responseSuccess: null as ((response: unknown) => unknown) | null,
    responseError: null as ((error: unknown) => unknown) | null,
  };

  const instance = vi.fn().mockImplementation(() => Promise.resolve({ data: "retry-ok" })) as unknown as AxiosInstance;
  instance.interceptors = {
    response: {
      use(
        onSuccess: (response: unknown) => unknown,
        onError: (error: unknown) => unknown,
      ) {
        handlers.responseSuccess = onSuccess;
        handlers.responseError = onError;
        return 0;
      },
    },
  } as never;

  addAuthRefreshInterceptor(instance);

  return { handlers, instance };
}

describe("addAuthRefreshInterceptor", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    useAuthStore.setState({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
    });
  });

  describe("Regression Tests — Auth endpoints exclusion", () => {
    it("does not attempt refresh when 401 occurs on /api/v1/auth/google/", async () => {
      const postSpy = vi.spyOn(Axios, "post");
      const { handlers } = createMockInstance();
      const config = { url: "/api/v1/auth/google/" } as InternalAxiosRequestConfig;
      const error = new AxiosError("Unauthorized", "ERR_BAD_REQUEST", config, undefined, {
        status: 401,
        data: { message: "Token do Google inválido" },
        statusText: "Unauthorized",
        headers: {} as never,
        config,
      });

      const result = handlers.responseError?.(error);
      await expect(result).rejects.toBe(error);

      expect(postSpy).not.toHaveBeenCalled();
    });

    it("does not attempt refresh when 401 occurs on /api/v1/auth/token/", async () => {
      const postSpy = vi.spyOn(Axios, "post");
      const { handlers } = createMockInstance();
      const config = { url: "/api/v1/auth/token/" } as InternalAxiosRequestConfig;
      const error = new AxiosError("Unauthorized", "ERR_BAD_REQUEST", config, undefined, {
        status: 401,
        data: { message: "Credenciais inválidas" },
        statusText: "Unauthorized",
        headers: {} as never,
        config,
      });

      const result = handlers.responseError?.(error);
      await expect(result).rejects.toBe(error);

      expect(postSpy).not.toHaveBeenCalled();
    });

    it("does not attempt refresh when 401 occurs on /api/v1/auth/register/", async () => {
      const postSpy = vi.spyOn(Axios, "post");
      const { handlers } = createMockInstance();
      const config = { url: "/api/v1/auth/register/" } as InternalAxiosRequestConfig;
      const error = new AxiosError("Unauthorized", "ERR_BAD_REQUEST", config, undefined, {
        status: 401,
        data: { message: "Erro no cadastro" },
        statusText: "Unauthorized",
        headers: {} as never,
        config,
      });

      const result = handlers.responseError?.(error);
      await expect(result).rejects.toBe(error);

      expect(postSpy).not.toHaveBeenCalled();
    });
  });

  describe("Non-401 and Non-Auth handling", () => {
    it("passes non-401 errors through without attempting refresh", async () => {
      const postSpy = vi.spyOn(Axios, "post");
      const { handlers } = createMockInstance();
      const config = { url: "/api/v1/weddings/" } as InternalAxiosRequestConfig;
      const error = new AxiosError("Not Found", "ERR_BAD_REQUEST", config, undefined, {
        status: 404,
        data: {},
        statusText: "Not Found",
        headers: {} as never,
        config,
      });

      const result = handlers.responseError?.(error);
      await expect(result).rejects.toBe(error);

      expect(postSpy).not.toHaveBeenCalled();
    });

    it("logs out and rejects normalized error when 401 on protected route and refreshToken is absent", async () => {
      const { handlers } = createMockInstance();
      const config = { url: "/api/v1/weddings/" } as InternalAxiosRequestConfig;
      const error = new AxiosError("Unauthorized", "ERR_BAD_REQUEST", config, undefined, {
        status: 401,
        data: {},
        statusText: "Unauthorized",
        headers: {} as never,
        config,
      });

      const result = handlers.responseError?.(error);
      await expect(result).rejects.toSatisfy((err: Error) => {
        return err.message.includes("Sessão irrecuperável: Refresh token ausente");
      });

      expect(useAuthStore.getState().isAuthenticated).toBe(false);
      expect(useAuthStore.getState().accessToken).toBeNull();
    });

    it("refreshes token successfully when 401 occurs on protected endpoint with valid refreshToken", async () => {
      useAuthStore.setState({
        accessToken: "old-access",
        refreshToken: "valid-refresh",
        user: { id: 1, email: "user@test.com", first_name: "Test", last_name: "User" },
        isAuthenticated: true,
      });

      const postSpy = vi.spyOn(Axios, "post").mockResolvedValueOnce({
        data: { access: "new-access", refresh: "new-refresh" },
      });

      const { handlers } = createMockInstance();
      const mockConfig = {
        url: "/api/v1/weddings/",
        headers: {},
      } as InternalAxiosRequestConfig;

      const error = new AxiosError("Unauthorized", "ERR_BAD_REQUEST", mockConfig, undefined, {
        status: 401,
        data: {},
        statusText: "Unauthorized",
        headers: {} as never,
        config: mockConfig,
      });

      const result = await handlers.responseError?.(error);

      expect(postSpy).toHaveBeenCalledWith(
        "/api/v1/auth/refresh/",
        { refresh: "valid-refresh" },
        expect.objectContaining({ timeout: 5000 }),
      );

      expect(useAuthStore.getState().accessToken).toBe("new-access");
      expect(useAuthStore.getState().refreshToken).toBe("new-refresh");
      expect(result).toEqual({ data: "retry-ok" });
    });
  });
});
