import { test as base, Page, APIRequestContext } from "@playwright/test";

/**
 * Key used to store authentication state in localStorage.
 */
const AUTH_STORAGE_KEY = "wedding-auth-storage";

/**
 * The base URL for the backend API, falling back to localhost if not specified.
 */
const API_BASE_URL = process.env.VITE_API_URL || "http://localhost:8000";

/**
 * Interface defining the custom Playwright fixtures for authenticated pages.
 */
export interface AuthFixtures {
  /** Page fixture for an authenticated Planner user. */
  authenticatedPage: Page;
  /** Page fixture for an authenticated Admin user. */
  adminPage: Page;
}

/**
 * Helper function to perform a backend login request, inject the token payload
 * into the browser's localStorage, and navigate directly to the dashboard.
 *
 * @param page The Playwright Page instance.
 * @param request The Playwright APIRequestContext instance.
 * @param email The user email used to authenticate.
 * @returns A promise resolving to the prepared Page instance.
 */
async function loginAndSetupPage(page: Page, request: APIRequestContext, email: string) {
  await page.goto("/");
  const response = await request.post(`${API_BASE_URL}/api/v1/auth/token/`, {
    data: {
      email,
      password: "password123", // pragma: allowlist secret
    },
  });
  if (!response.ok()) {
    throw new Error(`Failed to log in as ${email}: ${response.statusText()}`);
  }
  const data = await response.json();
  await page.evaluate(({ key, authData }) => {
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
  }, { key: AUTH_STORAGE_KEY, authData: data });
  await page.goto("/dashboard");
  await page.waitForURL("**/dashboard");
  return page;
}

/**
 * Extended Playwright test instance equipped with authentication fixtures.
 */
export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page, request }, run) => {
    const authPage = await loginAndSetupPage(page, request, "planner@example.com");
    await run(authPage);
  },

  adminPage: async ({ page, request }, run) => {
    const authPage = await loginAndSetupPage(page, request, "admin@admin.com");
    await run(authPage);
  },
});

/**
 * Re-export Playwright's expect assertion utility.
 */
export { expect } from "@playwright/test";
