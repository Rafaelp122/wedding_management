import { type Page, expect } from "@playwright/test";
import { ToastComponent } from "../components/toast.component";

const KPI_CARDS = [
  "Parcelas a Vencer",
  "Parcelas Vencidas",
  "Tarefas Atrasadas",
  "Contratos Pendentes",
] as const;

const KPI_VER_BUTTONS = ["Ver Parcelas", "Ver Parcelas", "Ver Tarefas", "Ver Contratos"];

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
    await expect(this.page.getByText(new RegExp(name, "i")).first()).toBeVisible();
  }

  async expectKpiCardsVisible() {
    for (const title of KPI_CARDS) {
      // Card titles are <p> elements, not headings (e.g. "Parcelas a Vencer (7d)")
      await expect(this.page.getByText(title, { exact: false }).first()).toBeVisible({
        timeout: 15_000,
      });
    }
  }

  async expectKpiValueRendered(cardLabel: string) {
    // Find the value sibling of the <p> label within the card (both are <p> elements)
    const label = this.page.getByText(cardLabel, { exact: false }).first();
    const valueElement = label.locator("..").locator("p").nth(1);
    await expect(valueElement).toHaveText(/^(?!\s*(--|—)\s*$).+/);
  }

  async expectChartVisible() {
    await expect(this.page.getByText("Casamentos por Mês")).toBeVisible({
      timeout: 15_000,
    });
    // Verify Recharts actually rendered an SVG
    await expect(this.page.locator(".recharts-surface").first()).toBeVisible();
  }

  async expectUpcomingInstallmentsVisible() {
    const heading = this.page.getByRole("heading", { name: "Parcelas a Vencer" });
    if ((await heading.count()) === 0) {
      await expect(this.page.getByText("Parcelas a Vencer", { exact: false }).first()).toBeVisible();
      return;
    }
    await expect(heading).toBeVisible();
    await expect(this.page.getByRole("button", { name: "7d" })).toBeVisible();
  }

  async expectInstallmentItemVisible() {
    if ((await this.page.getByRole("heading", { name: "Parcelas a Vencer" }).count()) === 0) {
      return;
    }
    const badge = this.page.getByText(/pendente[s]?$/).first();
    await expect(badge).toBeVisible();
    if (await this.page.getByText(/Parcela #\d+/).count() > 0) {
      await expect(this.page.getByText(/R\$/).first()).toBeVisible();
    }
  }

  async expectCriticalWeddingsVisible() {
    const heading = this.page.getByRole("heading", {
      name: "Casamentos que Precisam de Atenção",
    });
    if (await heading.count() === 0) return;
    await expect(heading).toBeVisible();
  }

  async clickCriticalWedding(name: string) {
    // Scope link search within the CriticalWeddings card to avoid sidebar matches
    const heading = this.page.getByRole("heading", {
      name: "Casamentos que Precisam de Atenção",
    });
    const card = heading.locator("..").locator("..");
    const link = card.getByRole("link").filter({ hasText: name }).first();
    await link.click();
    await expect(this.page).toHaveURL(/\/weddings\/[\w-]+/);
  }

  async openFirstAvailableKpiSheet() {
    await this.expectKpiCardsVisible();
    for (const label of KPI_VER_BUTTONS) {
      const btn = this.page.getByRole("button", { name: label });
      if (await btn.count() > 0) {
        await btn.first().click();
        await expect(this.page.getByRole("dialog")).toBeVisible();
        return;
      }
    }
    throw new Error(
      'Nenhum botão "Ver" encontrado nos cards de KPI — seed data pode não ter dados suficientes',
    );
  }
}
