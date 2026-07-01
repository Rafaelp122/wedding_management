import { describe, expect, it, beforeEach } from "vitest";
import { useAuthStore } from "@/stores/authStore";
import type { UserDataOut } from "@/api/generated/v1/models/userDataOut";

const mockUser: UserDataOut = {
  id: 1,
  first_name: "Test",
  last_name: "User",
  email: "test@email.com",
};

function resetStore() {
  useAuthStore.setState({
    accessToken: null,
    refreshToken: null,
    user: null,
    isAuthenticated: false,
  });
  localStorage.clear();
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

    it("persists state to localStorage", () => {
      useAuthStore.getState().login("access-1", "refresh-1", mockUser);

      const storedValue = localStorage.getItem("wedding-auth-storage");
      expect(storedValue).not.toBeNull();

      const parsed = JSON.parse(storedValue!);
      expect(parsed.state.accessToken).toBe("access-1");
      expect(parsed.state.user).toEqual(mockUser);
      expect(parsed.state.isAuthenticated).toBe(true);
    });
  });

  describe("logout", () => {
    it("clears all auth data from state and localStorage", () => {
      useAuthStore.getState().login("access-1", "refresh-1", mockUser);
      useAuthStore.getState().logout();

      const state = useAuthStore.getState();
      expect(state.accessToken).toBeNull();
      expect(state.refreshToken).toBeNull();
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);

      const storedValue = localStorage.getItem("wedding-auth-storage");
      const parsed = JSON.parse(storedValue!);
      expect(parsed.state.accessToken).toBeNull();
      expect(parsed.state.isAuthenticated).toBe(false);
    });
  });

  describe("rehydration", () => {
    it("initializes state from localStorage", async () => {
      const persistedState = {
        state: {
          accessToken: "stored-access",
          refreshToken: "stored-refresh",
          user: mockUser,
          isAuthenticated: true,
        },
        version: 0,
      };
      localStorage.setItem(
        "wedding-auth-storage",
        JSON.stringify(persistedState),
      );

      // We trigger a manual rehydration because the store is already initialized in the test environment
      await useAuthStore.persist.rehydrate();

      const state = useAuthStore.getState();
      expect(state.accessToken).toBe("stored-access");
      expect(state.refreshToken).toBe("stored-refresh");
      expect(state.user).toEqual(mockUser);
      expect(state.isAuthenticated).toBe(true);
    });
  });

  describe("updateTokens", () => {
    it("updates access token and keeps user", () => {
      useAuthStore.getState().login("access-1", "refresh-1", mockUser);
      useAuthStore.getState().updateTokens("access-2");

      const state = useAuthStore.getState();
      expect(state.accessToken).toBe("access-2");
      expect(state.refreshToken).toBe("refresh-1");
      expect(state.user).toEqual(mockUser);
    });

    it("updates both tokens and keeps user", () => {
      useAuthStore.getState().login("access-1", "refresh-1", mockUser);
      useAuthStore.getState().updateTokens("access-3", "refresh-3");

      const state = useAuthStore.getState();
      expect(state.accessToken).toBe("access-3");
      expect(state.refreshToken).toBe("refresh-3");
      expect(state.user).toEqual(mockUser);
    });
  });

  describe("updateUser", () => {
    it("merges partial user data and keeps tokens", () => {
      useAuthStore.getState().login("access-1", "refresh-1", mockUser);
      useAuthStore.getState().updateUser({ first_name: "Updated" });

      const state = useAuthStore.getState();
      expect(state.user?.first_name).toBe("Updated");
      expect(state.user?.email).toBe("test@email.com");
      expect(state.accessToken).toBe("access-1");
      expect(state.refreshToken).toBe("refresh-1");
    });

    it("does nothing when user is null", () => {
      useAuthStore.getState().updateUser({ first_name: "Nope" });
      expect(useAuthStore.getState().user).toBeNull();
    });
  });
});
