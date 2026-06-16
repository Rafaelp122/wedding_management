import { type Page, type Locator, expect } from "@playwright/test";

export class FormDialogComponent {
  readonly dialog: Locator;

  constructor(private readonly page: Page) {
    this.dialog = this.page.getByRole("dialog");
  }

  async fillField(label: string, value: string) {
    await this.page.getByLabel(label).fill(value);
  }

  async fillSelectField(label: string, optionLabel: string) {
    await this.page.getByLabel(label).click();
    await this.page.getByRole("option", { name: optionLabel }).click();
  }

  async submit() {
    const submitButton = this.dialog.getByRole("button", { name: /^(Criar|Salvar)/ });
    await submitButton.click();
  }

  async cancel() {
    await this.dialog.getByRole("button", { name: "Cancelar" }).click();
  }

  async expectVisible(title: string | RegExp) {
    await expect(this.dialog.getByRole("heading", { name: title })).toBeVisible();
  }

  async expectClosed() {
    await expect(this.dialog).not.toBeVisible();
  }
}
