import { Page, Locator, expect } from "@playwright/test";

export class ToastComponent {
  readonly toastContainer: Locator;

  constructor(private readonly page: Page) {
    this.toastContainer = this.page.locator("[data-sonner-toast], [role='status'], [role='alert']");
  }

  async expectSuccess(message: string | RegExp) {
    const successToast = this.toastContainer.filter({ hasText: message });
    await expect(successToast).toBeVisible();
  }

  async expectError(message: string | RegExp) {
    const errorToast = this.toastContainer.filter({ hasText: message });
    await expect(errorToast).toBeVisible();
  }
}
