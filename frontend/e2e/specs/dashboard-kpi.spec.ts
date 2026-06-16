import { test, expect } from "../fixtures/auth.fixture";
import { DashboardPage } from "../pages/dashboard.page";

test.describe("Dashboard KPIs", () => {
  test("@critical Dashboard carrega com todos os cards de KPI visíveis", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const dashboard = new DashboardPage(page);

    await dashboard.goto();
    await dashboard.expectGreeting("Planner");
    await dashboard.expectKpiCardsVisible();
  });

  test("@critical Cards de KPI exibem valores corretos (não '0' ou '--')", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const dashboard = new DashboardPage(page);

    await dashboard.goto();
    await dashboard.expectKpiValueNonZero("Parcelas a Vencer");
    await dashboard.expectKpiValueNonZero("Parcelas Vencidas");
    await dashboard.expectKpiValueNonZero("Tarefas Atrasadas");
    await dashboard.expectKpiValueNonZero("Contratos Pendentes");
  });

  test("@critical Link 'Ver' nos cards de KPI navega para Sheet", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const dashboard = new DashboardPage(page);

    await dashboard.goto();
    await dashboard.openKpiSheet("Ver Parcelas");
  });

  test("@regression Gráfico de casamentos mensais renderiza com dados", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const dashboard = new DashboardPage(page);

    await dashboard.goto();
    await dashboard.expectChartVisible();
  });

  test("@regression Lista de casamentos críticos visível com itens clicáveis", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const dashboard = new DashboardPage(page);

    await dashboard.goto();
    await dashboard.expectCriticalWeddingsVisible();

    // Click first critical wedding link and verify navigation
    const firstLink = page.getByText("Ver detalhes").first();
    await firstLink.click();
    await expect(page).toHaveURL(/\/weddings\/[\w-]+/);
  });

  test("@regression Próximas parcelas visíveis com valores corretos", async ({ authenticatedPage }) => {
    const page = authenticatedPage;
    const dashboard = new DashboardPage(page);

    await dashboard.goto();
    await dashboard.expectUpcomingInstallmentsVisible();
    await dashboard.expectInstallmentValue();
  });
});
