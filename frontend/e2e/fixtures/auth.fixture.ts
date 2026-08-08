import { test as base, Page } from "@playwright/test";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const PLANNER_STORAGE_PATH = path.resolve(__dirname, "../.auth/planner.json");
export const ADMIN_STORAGE_PATH = path.resolve(__dirname, "../.auth/admin.json");

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
 * Extended Playwright test instance equipped with pre-authenticated storageState fixtures.
 */
export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ browser }, run) => {
    const context = await browser.newContext({
      storageState: PLANNER_STORAGE_PATH,
    });
    const page = await context.newPage();
    await run(page);
    await context.close();
  },

  adminPage: async ({ browser }, run) => {
    const context = await browser.newContext({
      storageState: ADMIN_STORAGE_PATH,
    });
    const page = await context.newPage();
    await run(page);
    await context.close();
  },
});

/**
 * Re-export Playwright's expect assertion utility.
 */
export { expect } from "@playwright/test";
