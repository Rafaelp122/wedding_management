import { type Page, expect } from "@playwright/test";
import { ToastComponent } from "../components/toast.component";

const KPI_CARD_TITLES = [
  "Parcelas a Vencer",
  "Parcelas Vencidas",
  "Tarefas Atrasadas",
  "Contratos Pendentes",
] as const;

export class DashboardPage {
  readonly toast: ToastComponent;

  constructor(private readonly page: Page) {
    this.toast = new ToastComponent(page);
  }

  async goto() {
    await this.page.goto("/dashboard");
    await this.page.waitForURL("**/dashboard");
  }

  async expectGreeting(name: string) {
    await expect(this.page.getByText(new RegExp(name, "i"))).toBeVisible();
  }

  async expectKpiCardsVisible() {
    for (const title of KPI_CARD_TITLES) {
      await expect(
        this.page.getByRole("heading", { name: title, exact: true }),
      ).toBeVisible();
    }
  }

  async expectKpiValueNonZero(cardTitle: string) {
    const card = this.page.getByRole("heading", { name: cardTitle, exact: true }).locator("..").locator("..");
    const valueText = await card.innerText();
    expect(valueText).not.toContain("0");
    expect(valueText).not.toContain("—");
  }

  async openKpiSheet(buttonLabel: string) {
    await this.page.getByRole("button", { name: buttonLabel }).click();
    await expect(this.page.getByRole("dialog")).toBeVisible();
  }

  async expectCriticalWeddingsVisible() {
    await expect(
      this.page.getByRole("heading", { name: "Casamentos que Precisam de Atenção" }),
    ).toBeVisible();
  }

  async clickCriticalWedding(name: string) {
    const card = this.page.getByRole("link").filter({ hasText: name }).first();
    await card.click();
    await expect(this.page).toHaveURL(/\/weddings\/[\w-]+/);
  }

  async expectChartVisible() {
    await expect(
      this.page.getByRole("heading", { name: "Casamentos por Mês" }),
    ).toBeVisible();
  }

  async expectUpcomingInstallmentsVisible() {
    // "Parcelas a Vencer" appears in both KPI cards and UpcomingInstallments card.
    // Differentiate by checking for the period filter (7d, 14d, 30d) unique to UpcomingInstallments.
    await expect(this.page.getByRole("button", { name: "7d" })).toBeVisible();
    await expect(this.page.getByRole("button", { name: "14d" })).toBeVisible();
    await expect(this.page.getByRole("button", { name: "30d" })).toBeVisible();
  }

  async expectInstallmentValue() {
    await expect(
      this.page.getByRole("button", { name: "7d" }).locator("..").locator("..").getByText(/R\$/),
    ).toBeVisible();
  }
}
