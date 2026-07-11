/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import WeddingDetailPage from "@/features/weddings/pages/WeddingDetailPage";
import { createMockWedding } from "@/test-data";
import { useParams } from "react-router-dom";
import { useWeddingsRead } from "@/api/generated/v1/endpoints/weddings/weddings";
import { useDashboardWedding } from "@/api/generated/v1/endpoints/dashboard/dashboard";

const mockWedding = createMockWedding({
  bride_name: "Maria",
  groom_name: "João",
  date: "2026-09-20",
  location: "Fazenda Vila Rica, SP",
  expected_guests: 250,
  total_budget: 145000,
  template: "beach_6m",
});

// Mock useParams to control the uuid param independently of MemoryRouter
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<
    typeof import("react-router-dom")
  >("react-router-dom");
  return {
    ...actual,
    useParams: vi.fn(),
  };
});

vi.mock("@/features/weddings/components/EditWeddingDialog", () => ({
  EditWeddingDialog: ({ open, onSuccess, onOpenChange }: any) => {
    if (!open) return null;
    return (
      <div data-testid="edit-dialog">
        <button onClick={() => onSuccess()} data-testid="submit-success">Success</button>
        <button onClick={() => onOpenChange(false)} data-testid="close-dialog">Close</button>
      </div>
    );
  }
}));

describe("WeddingDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useDashboardWedding).mockReturnValue({
      data: {
        data: {
          tasks_completed: 68,
          tasks_total: 100,
          days_until_wedding: 30,
          budget_percentage_used: 10,
          contracts_signed: 1,
          contracts_total: 2,
          upcoming_installments: [],
          urgent_tasks: [],
          categories_summary: [],
        },
      },
      isLoading: false,
      error: null,
    } as any);
  });

  it("shows 'URL inválida' when uuid is undefined", () => {
    vi.mocked(useParams).mockReturnValue({});
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, { initialEntries: ["/weddings"] });

    expect(screen.getByText("URL inválida")).toBeInTheDocument();
    expect(
      screen.getByText(/nenhum uuid de casamento foi encontrado na url/i),
    ).toBeInTheDocument();
  });

  it("shows 'URL inválida' with back-to-list link", () => {
    vi.mocked(useParams).mockReturnValue({});
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, { initialEntries: ["/weddings"] });

    expect(
      screen.getByRole("link", { name: /voltar para lista/i }),
    ).toBeInTheDocument();
  });

  it("shows loading skeleton when isLoading is true", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("shows error alert on API error", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error("Erro de rede"),
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(
      screen.getByText("Erro ao carregar casamento"),
    ).toBeInTheDocument();
    expect(screen.getByText("Erro de rede")).toBeInTheDocument();
  });

  it("shows 'casamento não encontrado' when data loads but wedding is null", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: { data: undefined },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(
      screen.getByText("Casamento não encontrado"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /o casamento solicitado não foi encontrado ou você não tem permissão para acessá-lo/i,
      ),
    ).toBeInTheDocument();
  });

  it("shows wedding detail tabs and compact card when data loads", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: { data: mockWedding },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    vi.mocked(useDashboardWedding).mockReturnValue({
      data: {
        data: {
          tasks_completed: 68,
          tasks_total: 100,
          days_until_wedding: 30,
          budget_percentage_used: 10,
          contracts_signed: 1,
          contracts_total: 2,
          upcoming_installments: [],
          urgent_tasks: [],
          categories_summary: [],
        },
      },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useDashboardWedding>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(screen.getAllByText("João & Maria").length).toBeGreaterThan(0);
    expect(screen.getByText("Campestre")).toBeInTheDocument();
    expect(screen.getByText(/250 Convidados/i)).toBeInTheDocument();
    expect(screen.getByText("R$ 145k")).toBeInTheDocument();
    expect(screen.getByText("68%")).toBeInTheDocument();

    expect(screen.getByRole("tab", { name: /visão geral/i })).toBeInTheDocument();
    expect(
      screen.getByRole("tab", { name: /finanças/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("tab", { name: /logística/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("tab", { name: /planejamento/i }),
    ).toBeInTheDocument();
  });

  it("does not render the template badge when template is null", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: {
        data: {
          ...mockWedding,
          template: null,
        },
      },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(screen.queryByText("Campestre")).not.toBeInTheDocument();
    expect(screen.queryByText("Clássico")).not.toBeInTheDocument();
    expect(screen.queryByText("Intimista")).not.toBeInTheDocument();
  });

  it("renders budget and checklist skeletons when dashboard is loading", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: { data: mockWedding },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    vi.mocked(useDashboardWedding).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as unknown as ReturnType<typeof useDashboardWedding>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(screen.queryByText("R$ 145k")).not.toBeInTheDocument();
    expect(screen.queryByText("68%")).not.toBeInTheDocument();
  });

  it("shows fallback error message on API error with no message", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: {} as any,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(
      screen.getByText("Não foi possível carregar os dados do casamento."),
    ).toBeInTheDocument();
  });

  it("shows zero-state for expected guests when expected_guests is null/0", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: {
        data: {
          ...mockWedding,
          expected_guests: null,
        },
      },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(screen.getByText("— Convidados")).toBeInTheDocument();
  });

  it("calculates 0% checklist percentage when tasks_total is 0", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: { data: mockWedding },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    vi.mocked(useDashboardWedding).mockReturnValue({
      data: {
        data: {
          tasks_completed: 0,
          tasks_total: 0,
          days_until_wedding: 30,
          budget_percentage_used: 10,
          contracts_signed: 1,
          contracts_total: 2,
          upcoming_installments: [],
          urgent_tasks: [],
          categories_summary: [],
        },
      },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useDashboardWedding>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("renders budget formatted when total_budget is under 1000", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: {
        data: {
          ...mockWedding,
          total_budget: 500,
        },
      },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(screen.getByText("R$ 500")).toBeInTheDocument();
  });

  it("opens edit dialog on pencil click and triggers query invalidation on success", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: { data: mockWedding },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    const editBtn = screen.getByTitle("Editar dados do casamento");
    await userEvent.click(editBtn);

    expect(screen.getByTestId("edit-dialog")).toBeInTheDocument();

    const successBtn = screen.getByTestId("submit-success");
    await userEvent.click(successBtn);

    expect(screen.queryByTestId("edit-dialog")).not.toBeInTheDocument();
  });

  it("renders with fallback budget, decimal budget, unknown template, and completed status style", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: {
        data: {
          ...mockWedding,
          total_budget: null,
          template: "unknown_template",
          status: "COMPLETED",
        },
      },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    const { rerender } = render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(screen.getByText("R$ —")).toBeInTheDocument();
    expect(screen.getByText("unknown_template")).toBeInTheDocument();
    expect(screen.getByText("✓")).toBeInTheDocument();

    // Rerender with decimal budget
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: {
        data: {
          ...mockWedding,
          total_budget: 145500,
        },
      },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    rerender(<WeddingDetailPage />);
    expect(screen.getByText("R$ 145.5k")).toBeInTheDocument();
  });
});
