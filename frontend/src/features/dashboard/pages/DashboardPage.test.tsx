import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import DashboardPage from "@/features/dashboard/pages/DashboardPage";
import { server } from "@/mocks/server";

vi.mock("recharts", () => ({
  ResponsiveContainer: ({
    children,
    width,
    height,
  }: {
    children: React.ReactNode;
    width?: string | number;
    height?: string | number;
  }) => <div data-testid="recharts-container" style={{ width, height }}>{children}</div>,
  BarChart: ({
    children,
    data,
  }: {
    children: React.ReactNode;
    data: unknown[];
  }) => <div data-testid="bar-chart" data-items={data.length}>{children}</div>,
  Bar: ({ dataKey, name }: { dataKey: string; name?: string }) => (
    <div data-testid={`bar-${dataKey}`}>{name}</div>
  ),
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  XAxis: ({ dataKey }: { dataKey: string }) => (
    <div data-testid="x-axis" data-datakey={dataKey} />
  ),
  YAxis: () => <div data-testid="y-axis" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
}));

describe("DashboardPage", () => {
  it("shows loading skeletons initially", () => {
    render(<DashboardPage />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders dashboard after loading", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(
        screen.getByText(/Aqui está o panorama financeiro e de eventos para hoje/i),
      ).toBeInTheDocument();
    });
  });

  it("shows year selector", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("Casamentos por Mês")).toBeInTheDocument();
    }, { timeout: 5000 });

    const currentYear = new Date().getFullYear().toString();
    expect(screen.getByText(currentYear)).toBeInTheDocument();
  });

  it("shows stats cards after loading", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(
        screen.getByText("Parcelas Vencidas"),
      ).toBeInTheDocument();
    });
  });

  it("shows chart and appointments sections", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(
        screen.getByText("Casamentos por Mês"),
      ).toBeInTheDocument();
      expect(
        screen.getByText("Agenda"),
      ).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it("shows error state when API fails", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({ detail: "Erro ao carregar painel" }, { status: 500 }),
      ),
    );

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("Erro")).toBeInTheDocument();
      expect(
        screen.getByText("Erro ao carregar painel"),
      ).toBeInTheDocument();
    });
  });

  it("allows changing year with selector", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("Casamentos por Mês")).toBeInTheDocument();
    }, { timeout: 5000 });

    const user = userEvent.setup();
    const prevBtn = screen.getByRole("button", { name: /ano anterior/i });
    await user.click(prevBtn);

    const lastYear = new Date().getFullYear() - 1;
    expect(screen.getByText(lastYear.toString())).toBeInTheDocument();
  });
});
