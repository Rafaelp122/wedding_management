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

export function generateWeddingData(): CreateWeddingData {
  return {
    groom_name: faker.person.fullName(),
    bride_name: faker.person.fullName(),
    date: faker.date.future({ years: 1 }).toISOString().split("T")[0],
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

  async createWedding(data: CreateWeddingData) {
    await this.page.getByRole("button", { name: "Novo Casamento" }).click();
    await this.formDialog.expectVisible("Novo Casamento");
    await this.formDialog.fillField("Nome do Noivo", data.groom_name);
    await this.formDialog.fillField("Nome da Noiva", data.bride_name);
    await this.formDialog.fillField("Data do Casamento", data.date);
    await this.formDialog.fillField("Número de Convidados (Opcional)", String(data.expected_guests ?? ""));
    await this.formDialog.fillField("Local", data.location);
    await this.formDialog.fillSelectField("Modelo de Cronograma", "Nenhum (Começar do zero)");
    await this.formDialog.submit();
    await this.formDialog.expectClosed();
  }

  async editWedding(name: string, data: Partial<CreateWeddingData>) {
    const row = this.page.getByRole("row").filter({ hasText: name });
    await row.getByRole("button", { name: "Editar casamento" }).click();
    await this.formDialog.expectVisible("Editar Casamento");

    if (data.groom_name) await this.formDialog.fillField("Nome do Noivo", data.groom_name);
    if (data.bride_name) await this.formDialog.fillField("Nome da Noiva", data.bride_name);
    if (data.date) await this.formDialog.fillField("Data do Casamento", data.date);
    if (data.location) await this.formDialog.fillField("Local", data.location);
    if (data.expected_guests) {
      await this.formDialog.fillField("Número de Convidados (Opcional)", String(data.expected_guests));
    }

    await this.formDialog.submit();
    await this.formDialog.expectClosed();
  }

  async deleteWedding(name: string) {
    const row = this.page.getByRole("row").filter({ hasText: name });
    await row.getByRole("button", { name: "Deletar casamento" }).click();
    await this.confirmDelete.expectVisible();
    await this.confirmDelete.confirm(name);
  }

  async viewWedding(name: string) {
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
    const row = this.page.getByRole("row").filter({ hasText: name });
    await expect(row).toBeVisible();
  }

  async expectRowNotVisible(name: string) {
    const row = this.page.getByRole("row").filter({ hasText: name });
    await expect(row).not.toBeVisible();
  }

  async expectToastSuccess(message: string | RegExp) {
    await this.toast.expectSuccess(message);
  }
}
