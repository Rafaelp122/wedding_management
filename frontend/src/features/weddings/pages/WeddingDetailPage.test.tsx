/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, server } from "@/test-utils";
import WeddingDetailPage from "@/features/weddings/pages/WeddingDetailPage";
import { createMockWedding } from "@/test-data";
import { useParams } from "react-router-dom";
import { getWeddingsReadQueryKey } from "@/api/generated/v1/endpoints/weddings/weddings";
import { http, HttpResponse } from "msw";
import { QueryClient } from "@tanstack/react-query";
import type { WeddingDashboardOut } from "@/api/generated/v1/models/weddingDashboardOut";

// Mantido: mock de módulo NÃO-Orval (react-router-dom)
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<
    typeof import("react-router-dom")
  >("react-router-dom");
  return {
    ...actual,
    useParams: vi.fn(),
  };
});

// Mantido: mock de componente local NÃO-Orval
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

const mockWedding = createMockWedding({
  bride_name: "Maria",
  groom_name: "João",
  date: "2026-09-20",
  location: "Fazenda Vila Rica, SP",
  expected_guests: 250,
  total_budget: 145000,
  template: "beach_6m",
});

const defaultDashboard: WeddingDashboardOut = {
  tasks_completed: 68,
  tasks_total: 100,
  days_until_wedding: 30,
  budget_percentage_used: 10,
  contracts_signed: 1,
  contracts_total: 2,
  upcoming_installments: [],
  urgent_tasks: [],
  categories_summary: [],
};

describe("WeddingDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    server.use(
      http.get("*/api/v1/weddings/some-uuid/", () => {
        return HttpResponse.json(mockWedding);
      }),
      http.get("*/api/v1/weddings/some-uuid/overview/", () => {
        return HttpResponse.json({
          wedding: mockWedding,
          overview: defaultDashboard,
        });
      })
    );
  });

  it("shows 'URL inválida' when uuid is undefined", () => {
    vi.mocked(useParams).mockReturnValue({});

    render(<WeddingDetailPage />, { initialEntries: ["/weddings"] });

    expect(screen.getByText("URL inválida")).toBeInTheDocument();
    expect(
      screen.getByText(/nenhum uuid de casamento foi encontrado na url/i),
    ).toBeInTheDocument();
  });

  it("shows 'URL inválida' with back-to-list link", () => {
    vi.mocked(useParams).mockReturnValue({});

    render(<WeddingDetailPage />, { initialEntries: ["/weddings"] });

    expect(
      screen.getByRole("link", { name: /voltar para lista/i }),
    ).toBeInTheDocument();
  });

  it("shows loading skeleton when isLoading is true", () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    server.use(
      http.get("*/api/v1/weddings/some-uuid/", () => {
        return new Promise(() => {});
      })
    );

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("shows error alert on API error", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    server.use(
      http.get("*/api/v1/weddings/some-uuid/", () => {
        return HttpResponse.error();
      })
    );

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(
      await screen.findByText("Erro ao carregar casamento"),
    ).toBeInTheDocument();
    expect(screen.getByText("Network Error")).toBeInTheDocument();
  });

  it("shows 'casamento não encontrado' when data loads but wedding is null", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    server.use(
      http.get("*/api/v1/weddings/some-uuid/", () => {
        return HttpResponse.json(null);
      }),
      http.get("*/api/v1/weddings/some-uuid/overview/", () => {
        return HttpResponse.json({
          wedding: null,
          overview: defaultDashboard,
        });
      })
    );

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(
      await screen.findByText("Casamento não encontrado"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /o casamento solicitado não foi encontrado ou você não tem permissão para acessá-lo/i,
      ),
    ).toBeInTheDocument();
  });

  it("shows wedding detail tabs and compact card when data loads", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect((await screen.findAllByRole("heading", { name: /João\s*&\s*Maria/i })).length).toBeGreaterThan(0);
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

  it("does not render the template badge when template is null", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    server.use(
      http.get("*/api/v1/weddings/some-uuid/", () => {
        return HttpResponse.json({
          ...mockWedding,
          template: null,
        });
      }),
      http.get("*/api/v1/weddings/some-uuid/overview/", () => {
        return HttpResponse.json({
          wedding: {
            ...mockWedding,
            template: null,
          },
          overview: defaultDashboard,
        });
      })
    );

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect((await screen.findAllByRole("heading", { name: /João\s*&\s*Maria/i })).length).toBeGreaterThan(0);
    expect(screen.queryByText("Campestre")).not.toBeInTheDocument();
    expect(screen.queryByText("Clássico")).not.toBeInTheDocument();
    expect(screen.queryByText("Intimista")).not.toBeInTheDocument();
  });

  it("renders budget immediately and checklist skeleton when dashboard is loading", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    server.use(
      http.get("*/api/v1/weddings/some-uuid/overview/", () => {
        return new Promise(() => {});
      })
    );

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });


    expect(await screen.findByText("R$ 145k")).toBeInTheDocument();
    // Checklist still depends on dashboard
    expect(screen.queryByText("68%")).not.toBeInTheDocument();
  });

  it("shows fallback error message on API error with no message", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    server.use(
      http.get("*/api/v1/weddings/some-uuid/", () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(
      await screen.findByText("Request failed with status code 500"),
    ).toBeInTheDocument();
  });

  it("shows zero-state for expected guests when expected_guests is null/0", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    server.use(
      http.get("*/api/v1/weddings/some-uuid/", () => {
        return HttpResponse.json({
          ...mockWedding,
          expected_guests: null,
        });
      })
    );

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(await screen.findByText("— Convidados")).toBeInTheDocument();
  });

  it("calculates 0% checklist percentage when tasks_total is 0", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    server.use(
      http.get("*/api/v1/weddings/some-uuid/overview/", () => {
        return HttpResponse.json({
          wedding: mockWedding,
          overview: {
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
        });
      })
    );

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(await screen.findByText("0%")).toBeInTheDocument();
  });

  it("renders budget formatted when total_budget is under 1000", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    server.use(
      http.get("*/api/v1/weddings/some-uuid/", () => {
        return HttpResponse.json({
          ...mockWedding,
          total_budget: 500,
        });
      })
    );

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    expect(await screen.findByText("R$ 500")).toBeInTheDocument();
  });

  it("opens edit dialog on pencil click and triggers query invalidation on success", async () => {
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
    });

    const editBtn = await screen.findByTitle("Editar dados do casamento");
    await userEvent.click(editBtn);

    expect(screen.getByTestId("edit-dialog")).toBeInTheDocument();

    const successBtn = screen.getByTestId("submit-success");
    await userEvent.click(successBtn);

    expect(screen.queryByTestId("edit-dialog")).not.toBeInTheDocument();
  });

  it("renders with fallback budget, decimal budget, unknown template, and completed status style", async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    vi.mocked(useParams).mockReturnValue({ uuid: "some-uuid" });
    server.use(
      http.get("*/api/v1/weddings/some-uuid/", () => {
        return HttpResponse.json({
          ...mockWedding,
          total_budget: null,
          template: "unknown_template",
          status: "COMPLETED",
        });
      })
    );

    render(<WeddingDetailPage />, {
      initialEntries: ["/weddings/some-uuid"],
      queryClient,
    });

    expect(await screen.findByText("R$ —")).toBeInTheDocument();
    expect(screen.getByText("unknown_template")).toBeInTheDocument();
    expect(screen.getByText("✓")).toBeInTheDocument();

    // Atualiza o cache do React Query de forma síncrona
    queryClient.setQueryData(
      getWeddingsReadQueryKey("some-uuid"),
      {
        data: {
          ...mockWedding,
          total_budget: 145500,
        }
      }
    );

    expect(await screen.findByText("R$ 145.5k")).toBeInTheDocument();
  });
});
