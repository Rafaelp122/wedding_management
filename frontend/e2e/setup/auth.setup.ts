import { test as setup } from "@playwright/test";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const API_BASE_URL = process.env.VITE_API_URL || "http://localhost:8000";
const AUTH_STORAGE_KEY = "wedding-auth-storage";

export const PLANNER_STORAGE_PATH = path.resolve(__dirname, "../.auth/planner.json");
export const ADMIN_STORAGE_PATH = path.resolve(__dirname, "../.auth/admin.json");

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
