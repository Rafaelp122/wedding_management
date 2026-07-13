import { type Page, expect } from "@playwright/test";

export class WeddingDetailPage {
  constructor(private readonly page: Page) {}

  async expectHeading(groom: string, bride: string) {
    await expect(
      this.page.getByRole("heading", { level: 2, name: `${groom} & ${bride}` }).first(),
    ).toBeVisible();
  }

  async expectStatus(status: string) {
    await expect(this.page.getByText(status)).toBeVisible();
  }

  async goBack() {
    await this.page.getByRole("link", { name: "Casamentos" }).first().click();
    await expect(this.page).toHaveURL(/\/weddings$/);
  }

  async expectUrlMatch() {
    await expect(this.page).toHaveURL(/\/weddings\/[\w-]+/);
  }
}
