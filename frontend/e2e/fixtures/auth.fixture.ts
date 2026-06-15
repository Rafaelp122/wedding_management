/* eslint-disable react-hooks/rules-of-hooks */
import { test as base, Page } from "@playwright/test";

const API_URL = process.env.VITE_API_URL || "http://localhost:8000";

export interface AuthFixtures {
  authenticatedPage: Page;
  adminPage: Page;
  staffPage: Page;
}

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page, request }, use) => {
    // Navigate to page first to set correct origin in browser
    await page.goto("/");

    const response = await request.post(`${API_URL}/api/v1/auth/token/`, {
      data: {
        email: "planner@example.com",
        password: "password123", // pragma: allowlist secret
      },
    });

    if (!response.ok()) {
      throw new Error(`Failed to log in as planner: ${response.statusText()}`);
    }

    const data = await response.json();

    await page.evaluate((authData) => {
      localStorage.setItem(
        "wedding-auth-storage",
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
    }, data);

    await page.goto("/dashboard");
    await page.waitForURL("**/dashboard");

    await use(page);
  },

  adminPage: async ({ page, request }, use) => {
    await page.goto("/");

    const response = await request.post(`${API_URL}/api/v1/auth/token/`, {
      data: {
        email: "admin@admin.com",
        password: "password123", // pragma: allowlist secret
      },
    });

    if (!response.ok()) {
      throw new Error(`Failed to log in as admin: ${response.statusText()}`);
    }

    const data = await response.json();

    await page.evaluate((authData) => {
      localStorage.setItem(
        "wedding-auth-storage",
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
    }, data);

    await page.goto("/dashboard");
    await page.waitForURL("**/dashboard");

    await use(page);
  },

  staffPage: async ({ page, request }, use) => {
    await page.goto("/");

    const response = await request.post(`${API_URL}/api/v1/auth/token/`, {
      data: {
        email: "staff@example.com",
        password: "password123", // pragma: allowlist secret
      },
    });

    if (!response.ok()) {
      throw new Error(`Failed to log in as staff: ${response.statusText()}`);
    }

    const data = await response.json();

    await page.evaluate((authData) => {
      localStorage.setItem(
        "wedding-auth-storage",
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
    }, data);

    await page.goto("/dashboard");
    await page.waitForURL("**/dashboard");

    await use(page);
  },
});

export { expect } from "@playwright/test";
