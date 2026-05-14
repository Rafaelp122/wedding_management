import { describe, expect, it, beforeEach } from "vitest";
import { useAuthStore } from "@/stores/authStore";
import type { UserDataOut } from "@/api/generated/v1/models/userDataOut";

const mockUser: UserDataOut = {
  id: 1,
  name: "Test User",
  email: "test@email.com",
  company_name: "Acme",
  avatar_url: "",
};

function resetStore() {
  useAuthStore.setState({
    accessToken: null,
    refreshToken: null,
    user: null,
    isAuthenticated: false,
  });
}

describe("useAuthStore", () => {
  beforeEach(() => {
    resetStore();
  });

  describe("initial state", () => {
    it("has no tokens", () => {
      const state = useAuthStore.getState();
      expect(state.accessToken).toBeNull();
      expect(state.refreshToken).toBeNull();
    });

    it("has no user", () => {
      expect(useAuthStore.getState().user).toBeNull();
    });

    it("is not authenticated", () => {
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });
  });

  describe("login", () => {
    it("sets tokens and user", () => {
      useAuthStore.getState().login("access-1", "refresh-1", mockUser);

      const state = useAuthStore.getState();
      expect(state.accessToken).toBe("access-1");
      expect(state.refreshToken).toBe("refresh-1");
      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
    });
  });

  describe("logout", () => {
    it("clears all auth data", () => {
      useAuthStore.getState().login("access-1", "refresh-1", mockUser);
      useAuthStore.getState().logout();

      const state = useAuthStore.getState();
      expect(state.accessToken).toBeNull();
      expect(state.refreshToken).toBeNull();
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });
  });

  describe("updateTokens", () => {
    it("updates access token", () => {
      useAuthStore.getState().login("access-1", "refresh-1", mockUser);
      useAuthStore.getState().updateTokens("access-2");

      const state = useAuthStore.getState();
      expect(state.accessToken).toBe("access-2");
      expect(state.refreshToken).toBe("refresh-1");
      expect(state.user).toEqual(mockUser);
    });

    it("updates both tokens when refresh is provided", () => {
      useAuthStore.getState().login("access-1", "refresh-1", mockUser);
      useAuthStore.getState().updateTokens("access-3", "refresh-3");

      const state = useAuthStore.getState();
      expect(state.accessToken).toBe("access-3");
      expect(state.refreshToken).toBe("refresh-3");
    });
  });

  describe("updateUser", () => {
    it("merges partial user data", () => {
      useAuthStore.getState().login("access-1", "refresh-1", mockUser);
      useAuthStore.getState().updateUser({ name: "Updated Name" });

      const state = useAuthStore.getState();
      expect(state.user?.name).toBe("Updated Name");
      expect(state.user?.email).toBe("test@email.com");
    });

    it("does nothing when user is null", () => {
      useAuthStore.getState().updateUser({ name: "Nope" });
      expect(useAuthStore.getState().user).toBeNull();
    });
  });
});
