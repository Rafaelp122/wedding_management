import { type Page, type Locator, expect } from "@playwright/test";

export class ConfirmDeleteComponent {
  readonly dialog: Locator;
  readonly confirmInput: Locator;
  readonly confirmButton: Locator;

  constructor(private readonly page: Page) {
    this.dialog = this.page.getByRole("dialog");
    this.confirmInput = this.page.getByPlaceholder("Digite o nome aqui...");
    this.confirmButton = this.page.getByRole("button", { name: "Deletar Permanentemente" });
  }

  async confirm(itemName: string) {
    await this.confirmInput.fill(itemName);
    await this.confirmButton.click();
  }

  async cancel() {
    await this.dialog.getByRole("button", { name: "Cancelar" }).click();
  }

  async expectVisible() {
    await expect(this.dialog).toBeVisible();
  }
}
