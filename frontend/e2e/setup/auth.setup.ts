import { test as setup } from "@playwright/test";
import {
  API_BASE_URL,
  AUTH_STORAGE_KEY,
  PLANNER_STORAGE_PATH,
  ADMIN_STORAGE_PATH,
} from "../constants";

/**
 * Playwright setup project step to authenticate planner@example.com,
 * inject tokens into localStorage, and persist state to planner storageState file.
 */
setup("authenticate as planner", async ({ page, request }) => {
  await page.goto("/");
  const response = await request.post(`${API_BASE_URL}/api/v1/auth/token/`, {
    data: {
      email: "planner@example.com",
      password: "password123", // pragma: allowlist secret
    },
  });
  if (!response.ok()) {
    throw new Error(`Failed to log in as planner: ${response.statusText()}`);
  }
  const data = await response.json();
  await page.evaluate(
    ({ key, authData }) => {
      localStorage.setItem(
        key,
        JSON.stringify({
          state: {
            accessToken: authData.access,
            refreshToken: authData.refresh,
            user: authData.user,
            isAuthenticated: true,
          },
          version: 0,
        })
      );
    },
    { key: AUTH_STORAGE_KEY, authData: data }
  );

  await page.context().storageState({ path: PLANNER_STORAGE_PATH });
});

/**
 * Playwright setup project step to authenticate admin@admin.com,
 * inject tokens into localStorage, and persist state to admin storageState file.
 */
setup("authenticate as admin", async ({ page, request }) => {
  await page.goto("/");
  const response = await request.post(`${API_BASE_URL}/api/v1/auth/token/`, {
    data: {
      email: "admin@admin.com",
      password: "password123", // pragma: allowlist secret
    },
  });
  if (!response.ok()) {
    throw new Error(`Failed to log in as admin: ${response.statusText()}`);
  }
  const data = await response.json();
  await page.evaluate(
    ({ key, authData }) => {
      localStorage.setItem(
        key,
        JSON.stringify({
          state: {
            accessToken: authData.access,
            refreshToken: authData.refresh,
            user: authData.user,
            isAuthenticated: true,
          },
          version: 0,
        })
      );
    },
    { key: AUTH_STORAGE_KEY, authData: data }
  );

  await page.context().storageState({ path: ADMIN_STORAGE_PATH });
});
