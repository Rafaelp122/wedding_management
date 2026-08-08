import { test, expect } from "../fixtures/auth.fixture";
import { LoginPage } from "../pages/login.page";
import { SidebarComponent } from "../components/sidebar.component";
import { ToastComponent } from "../components/toast.component";
import { API_BASE_URL, AUTH_STORAGE_KEY } from "../constants";
import { injectAuthIntoStorage } from "../helpers/api.helper";

test.describe("Authentication Flow", () => {
  test("@smoke Login with valid credentials redirects to '/dashboard'", async ({ page }) => {
    const loginPage = new LoginPage(page);
    const toast = new ToastComponent(page);

    await loginPage.goto();
    await loginPage.login("planner@example.com", "password123");

    await expect(page).toHaveURL(/\/dashboard/);
    await toast.expectSuccess(/Bem-vindo/);
  });

  test("@smoke Unauthenticated access to '/dashboard' redirects to '/login'", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/);
  });

  test("@smoke Logout clears session and redirects to '/login'", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    await page.goto("/dashboard");
    const sidebar = new SidebarComponent(page);

    await sidebar.logout();
    await expect(page).toHaveURL(/\/login/);

    const storage = await page.evaluate((key) => localStorage.getItem(key), AUTH_STORAGE_KEY);
    if (storage) {
      const parsed = JSON.parse(storage);
      expect(parsed.state.isAuthenticated).toBe(false);
    }
  });

  test("@critical Login with invalid credentials shows 'E-mail ou senha incorretos.' error toast", async ({ page }) => {
    const loginPage = new LoginPage(page);
    const toast = new ToastComponent(page);

    await loginPage.goto();
    await loginPage.login("wrong@example.com", "wrongpassword");

    await toast.expectError(/E-mail ou senha incorretos\.|Credenciais inválidas ou conta desativada\./);
    await expect(page).toHaveURL(/\/login/);
  });

  test("@regression Transparent token refresh", async ({ page, request }) => {
    await page.goto("/");
    const loginRes = await request.post(`${API_BASE_URL}/api/v1/auth/token/`, {
      data: { email: "planner@example.com", password: "password123" }, // pragma: allowlist secret
    });
    const authData = await loginRes.json();
    await injectAuthIntoStorage(page, authData);

    let weddingsRequestCount = 0;
    await page.route("**/api/v1/weddings**", async (route) => {
      weddingsRequestCount++;
      if (weddingsRequestCount === 1) {
        await route.fulfill({
          status: 401,
          contentType: "application/json",
          body: JSON.stringify({ detail: "Token is invalid or expired" }),
        });
      } else {
        await route.continue();
      }
    });

    const refreshRequestPromise = page.waitForRequest(
      (request) =>
        request.url().includes("/api/v1/auth/refresh/") &&
        request.method() === "POST"
    );

    await page.goto("/weddings");

    const refreshRequest = await refreshRequestPromise;
    expect(refreshRequest).toBeDefined();

    await expect(page).toHaveURL(/\/weddings/);
    await expect(page.getByLabel("Menu do usuário")).toBeVisible();
  });

  test("@regression Admin page can bypass login and access dashboard", async ({ adminPage }) => {
    await adminPage.goto("/dashboard");
    await expect(adminPage).toHaveURL(/\/dashboard/);
    await expect(adminPage.getByText("admin@admin.com")).toBeVisible();
  });
});
