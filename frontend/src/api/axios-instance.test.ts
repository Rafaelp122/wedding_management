import { describe, expect, it, beforeEach, vi } from "vitest";
import { server } from "@/mocks/server";
import { createAxiosInstance } from "@/api/axios-instance";
import { useAuthStore } from "@/stores/authStore";

function resetAuthStore() {
  useAuthStore.setState({
    accessToken: null,
    refreshToken: null,
    user: null,
    isAuthenticated: false,
  });
}

function setAuthTokens(access: string, refresh: string) {
  useAuthStore.setState({
    accessToken: access,
    refreshToken: refresh,
    isAuthenticated: true,
  });
}

describe("createAxiosInstance", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    server.resetHandlers();
    resetAuthStore();
  });

  describe("request interceptor", () => {
    it("adds Bearer token when user is authenticated", async () => {
      setAuthTokens("access-123", "refresh-456");
      const instance = createAxiosInstance();

      const { http, HttpResponse } = await import("msw");
      let capturedAuthorization = "";
      server.use(
        http.get("*/api/v1/test-auth/", ({ request }) => {
          capturedAuthorization = request.headers.get("Authorization") || "";
          return HttpResponse.json({ ok: true });
        }),
      );

      await instance.get("/api/v1/test-auth/");
      expect(capturedAuthorization).toBe("Bearer access-123");
    });

    it("does not add Authorization header when token is absent", async () => {
      const instance = createAxiosInstance();

      const { http, HttpResponse } = await import("msw");
      let capturedAuthorization: string | null = null;
      server.use(
        http.get("*/api/v1/test-noauth/", ({ request }) => {
          capturedAuthorization = request.headers.get("Authorization");
          return HttpResponse.json({ ok: true });
        }),
      );

      await instance.get("/api/v1/test-noauth/");
      expect(capturedAuthorization).toBeNull();
    });
  });

  describe("refresh interceptor", () => {
    it("refreshes token on 401 and retries original request", async () => {
      setAuthTokens("expired-token", "valid-refresh");
      const instance = createAxiosInstance();

      const { http, HttpResponse } = await import("msw");
      let callCount = 0;

      server.use(
        http.get("*/api/v1/protected/", () => {
          callCount++;
          if (callCount === 1) {
            return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
          }
          return HttpResponse.json({ data: "success" });
        }),
        http.post("*/api/v1/auth/refresh/", () =>
          HttpResponse.json({
            access: "new-access-token",
            refresh: "new-refresh-token",
          }),
        ),
      );

      const response = await instance.get("/api/v1/protected/");

      expect(response.data).toEqual({ data: "success" });
      expect(callCount).toBe(2);
      expect(useAuthStore.getState().accessToken).toBe("new-access-token");
    });

    it("logs out when no refresh token is available", async () => {
      setAuthTokens("expired", "");
      const instance = createAxiosInstance();

      const { http, HttpResponse } = await import("msw");
      server.use(
        http.get("*/api/v1/protected/", () =>
          HttpResponse.json({ detail: "Unauthorized" }, { status: 401 }),
        ),
      );

      await expect(instance.get("/api/v1/protected/")).rejects.toThrow();
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });

    it("logs out when refresh request fails with 500", async () => {
      setAuthTokens("expired", "valid-refresh");
      const instance = createAxiosInstance();

      const { http, HttpResponse } = await import("msw");
      server.use(
        http.get("*/api/v1/protected/", () =>
          HttpResponse.json({ detail: "Unauthorized" }, { status: 401 }),
        ),
        http.post("*/api/v1/auth/refresh/", () =>
          HttpResponse.json({ detail: "Refresh failed" }, { status: 500 }),
        ),
      );

      await expect(instance.get("/api/v1/protected/")).rejects.toThrow();
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });

    it("logs out when refresh request fails with 400", async () => {
      setAuthTokens("expired", "invalid-refresh");
      const instance = createAxiosInstance();

      const { http, HttpResponse } = await import("msw");
      server.use(
        http.get("*/api/v1/protected/", () =>
          HttpResponse.json({ detail: "Unauthorized" }, { status: 401 }),
        ),
        http.post("*/api/v1/auth/refresh/", () =>
          HttpResponse.json({ detail: "Invalid token" }, { status: 400 }),
        ),
      );

      await expect(instance.get("/api/v1/protected/")).rejects.toThrow();
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });

    it("queues concurrent 401 requests and retries once", async () => {
      setAuthTokens("expired", "valid-refresh");
      const instance = createAxiosInstance();

      const { http, HttpResponse } = await import("msw");
      let dataCallCount = 0;

      server.use(
        http.get("*/api/v1/protected/", () => {
          dataCallCount++;
          if (dataCallCount <= 2) {
            return HttpResponse.json({ detail: "Unauthorized" }, { status: 401 });
          }
          return HttpResponse.json({ data: "success" });
        }),
        http.post("*/api/v1/auth/refresh/", () =>
          HttpResponse.json({
            access: "new-access",
            refresh: "new-refresh",
          }),
        ),
      );

      const [r1, r2] = await Promise.all([
        instance.get("/api/v1/protected/"),
        instance.get("/api/v1/protected/"),
      ]);

      expect(r1.data).toEqual({ data: "success" });
      expect(r2.data).toEqual({ data: "success" });
      expect(dataCallCount).toBe(4);
    });

    it("passes through non-401 responses unchanged", async () => {
      const instance = createAxiosInstance();

      const { http, HttpResponse } = await import("msw");
      server.use(
        http.get("*/api/v1/protected/", () =>
          HttpResponse.json({ data: "ok" }, { status: 200 }),
        ),
      );

      const response = await instance.get("/api/v1/protected/");
      expect(response.data).toEqual({ data: "ok" });
    });
  });
});
