import { type Page, expect } from "@playwright/test";
import { faker } from "@faker-js/faker";
import { FormDialogComponent } from "../components/form-dialog.component";
import { ConfirmDeleteComponent } from "../components/confirm-delete.component";
import { ToastComponent } from "../components/toast.component";

export interface CreateWeddingData {
  groom_name: string;
  bride_name: string;
  date: string;
  location: string;
  expected_guests?: number;
}

interface CreateWeddingOptions {
  focusRow?: boolean;
}

export function generateWeddingData(): CreateWeddingData {
  // Gera um ano futuro único e crescente baseado no timestamp atual (entre 2050 e 3050)
  const uniqueYear = 2050 + (Math.floor(Date.now() / 1000) % 1000);
  return {
    groom_name: faker.person.fullName(),
    bride_name: faker.person.fullName(),
    date: `${uniqueYear}-12-31`,
    location: faker.location.streetAddress(),
    expected_guests: faker.number.int({ min: 20, max: 500 }),
  };
}

export class WeddingsListPage {
  readonly formDialog: FormDialogComponent;
  readonly confirmDelete: ConfirmDeleteComponent;
  readonly toast: ToastComponent;

  constructor(private readonly page: Page) {
    this.formDialog = new FormDialogComponent(page);
    this.confirmDelete = new ConfirmDeleteComponent(page);
    this.toast = new ToastComponent(page);
  }

  async goto() {
    await this.page.goto("/weddings");
    await this.page.waitForURL("**/weddings");
  }

  async createWedding(data: CreateWeddingData, options: CreateWeddingOptions = {}) {
    const { focusRow = true } = options;
    await this.page.getByRole("button", { name: "Novo Casamento" }).click();
    await this.formDialog.expectVisible("Novo Casamento");
    await this.formDialog.fillField("Nome do Noivo", data.groom_name);
    await this.formDialog.fillField("Nome da Noiva", data.bride_name);
    await this.formDialog.fillField("Data do Casamento", data.date);
    await this.formDialog.fillField("Número de Convidados (Opcional)", String(data.expected_guests ?? ""));
    await this.formDialog.fillField("Local", data.location);
    await this.formDialog.fillSelectField("Modelo de Cronograma", "Nenhum (Começar do zero)");
    await this.formDialog.submit();
    await expect(this.page.getByText("Casamento criado com sucesso!").first()).toBeVisible();
    await this.formDialog.expectClosed();
    if (focusRow) {
      await this.searchWedding(`${data.groom_name} & ${data.bride_name}`);
    }
  }

  async searchWedding(name: string) {
    const searchTerm = name.split(" & ")[0];
    await this.page.getByRole("textbox", { name: "Buscar por noivos ou local..." }).fill(searchTerm);
  }

  async editWedding(name: string, data: Partial<CreateWeddingData>) {
    await this.searchWedding(name);
    const row = this.page.getByRole("row").filter({ hasText: name });
    await row.getByRole("button", { name: "Editar" }).click();
    await this.formDialog.expectVisible("Editar Casamento");

    if (data.groom_name) await this.formDialog.fillField("Nome do Noivo", data.groom_name);
    if (data.bride_name) await this.formDialog.fillField("Nome da Noiva", data.bride_name);
    if (data.date) await this.formDialog.fillField("Data do Casamento", data.date);
    if (data.location) await this.formDialog.fillField("Local", data.location);
    if (data.expected_guests) {
      await this.formDialog.fillField("Número de Convidados (Opcional)", String(data.expected_guests));
    }

    await this.formDialog.submit();
    await expect(this.page.getByText("Casamento atualizado com sucesso!").first()).toBeVisible();
    await this.formDialog.expectClosed();
  }

  async deleteWedding(name: string) {
    await this.searchWedding(name);
    const row = this.page.getByRole("row").filter({ hasText: name });
    await row.getByRole("button", { name: "Excluir" }).click();
    await this.confirmDelete.expectVisible();
    await this.confirmDelete.confirm(name);
  }

  async viewWedding(name: string) {
    await this.searchWedding(name);
    await this.page.getByRole("row").filter({ hasText: name }).click();
  }

  async filterByStatus(status: string) {
    await this.page.getByRole("combobox", { name: "Filtrar por status" }).click();
    await this.page.getByRole("option", { name: status }).click();
  }

  async nextPage() {
    await this.page.getByRole("button", { name: "Próximo" }).click();
  }

  async previousPage() {
    await this.page.getByRole("button", { name: "Anterior" }).click();
  }

  async expectRowVisible(name: string) {
    await this.searchWedding(name);
    const row = this.page.getByRole("row").filter({ hasText: name });
    await expect(row).toBeVisible();
  }

  async expectRowNotVisible(name: string) {
    await this.searchWedding(name);
    const row = this.page.getByRole("row").filter({ hasText: name });
    await expect(row).not.toBeVisible();
  }

  async expectToastSuccess(message: string | RegExp) {
    await this.toast.expectSuccess(message);
  }

  async expectHasNext() {
    await expect(this.page.getByRole("button", { name: "Próximo" })).toBeEnabled();
  }

  async expectHasPrevious() {
    await expect(this.page.getByRole("button", { name: "Anterior" })).toBeEnabled();
  }

  async expectNotHasPrevious() {
    await expect(this.page.getByRole("button", { name: "Anterior" })).toBeDisabled();
  }

  async expectNotHasNext() {
    await expect(this.page.getByRole("button", { name: "Próximo" })).toBeDisabled();
  }
}
