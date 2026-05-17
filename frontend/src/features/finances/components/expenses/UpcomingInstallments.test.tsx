import { describe, expect, it, vi, afterEach } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import { server } from "@/mocks/server";
import { createMockInstallment } from "@/test-data";
import { WeddingUpcomingInstallments } from "./UpcomingInstallments";

// ---------------------------------------------------------------------------
// Toast mocking – same pattern as EditExpenseDialog.test.tsx
// ---------------------------------------------------------------------------
const { toastSuccess, toastError } = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: { ...actual.toast, success: toastSuccess, error: toastError },
  };
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const WEDDING_UUID = "w-1";

function futureDate(daysFromNow: number): string {
  const d = new Date();
  d.setDate(d.getDate() + daysFromNow);
  return d.toISOString().slice(0, 10);
}

function pastDate(daysAgo: number): string {
  const d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return d.toISOString().slice(0, 10);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
describe("WeddingUpcomingInstallments", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading skeleton initially", () => {
    render(<WeddingUpcomingInstallments weddingUuid={WEDDING_UUID} />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("shows empty state when no installments exist", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
    );

    render(<WeddingUpcomingInstallments weddingUuid={WEDDING_UUID} />);

    await waitFor(() => {
      expect(
        screen.getByText(/Nenhuma parcela pendente/i),
      ).toBeInTheDocument();
    });
  });

  it("shows empty state when all installments are paid (filtered out)", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({
          items: [
            createMockInstallment({
              uuid: "inst-paid-1",
              installment_number: 1,
              status: "PAID",
            }),
          ],
          count: 1,
        }),
      ),
    );

    render(<WeddingUpcomingInstallments weddingUuid={WEDDING_UUID} />);

    await waitFor(() => {
      expect(
        screen.getByText(/Nenhuma parcela pendente/i),
      ).toBeInTheDocument();
    });
  });

  it("renders pending installments with correct details", async () => {
    const { http, HttpResponse } = await import("msw");
    const dueDate = futureDate(10);

    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({
          items: [
            createMockInstallment({
              uuid: "inst-1",
              installment_number: 1,
              amount: "500.00",
              due_date: dueDate,
              status: "PENDING",
            }),
          ],
          count: 1,
        }),
      ),
    );

    render(<WeddingUpcomingInstallments weddingUuid={WEDDING_UUID} />);

    await waitFor(() => {
      expect(screen.getByText(/Próximos Vencimentos/i)).toBeInTheDocument();
      expect(screen.getByText(/Parcela #1/)).toBeInTheDocument();
      expect(screen.getByText("R$ 500,00")).toBeInTheDocument();
      expect(screen.getByText("Pendente")).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /pagar/i }),
      ).toBeInTheDocument();
    });
  });

  it("renders multiple installments", async () => {
    const { http, HttpResponse } = await import("msw");

    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({
          items: [
            createMockInstallment({
              uuid: "inst-1",
              installment_number: 1,
              amount: "500.00",
              due_date: futureDate(5),
              status: "PENDING",
            }),
            createMockInstallment({
              uuid: "inst-2",
              installment_number: 2,
              amount: "750.50",
              due_date: pastDate(3),
              status: "OVERDUE",
            }),
          ],
          count: 2,
        }),
      ),
    );

    render(<WeddingUpcomingInstallments weddingUuid={WEDDING_UUID} />);

    await waitFor(() => {
      expect(screen.getByText(/Parcela #1/)).toBeInTheDocument();
      expect(screen.getByText(/Parcela #2/)).toBeInTheDocument();
      expect(screen.getByText("R$ 500,00")).toBeInTheDocument();
      expect(screen.getByText("R$ 750,50")).toBeInTheDocument();
    });
  });

  it("shows overdue badge for overdue installments", async () => {
    const { http, HttpResponse } = await import("msw");

    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({
          items: [
            createMockInstallment({
              uuid: "inst-overdue",
              installment_number: 1,
              amount: "300.00",
              due_date: pastDate(5),
              status: "OVERDUE",
            }),
          ],
          count: 1,
        }),
      ),
    );

    render(<WeddingUpcomingInstallments weddingUuid={WEDDING_UUID} />);

    await waitFor(() => {
      expect(screen.getByText("Atrasado")).toBeInTheDocument();
      const payButton = screen.getByRole("button", { name: /pagar/i });
      expect(payButton.className).toContain("destructive");
    });
  });

  it("marks installment as paid and shows success toast", async () => {
    const { http, HttpResponse } = await import("msw");
    const dueDate = futureDate(10);

    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({
          items: [
            createMockInstallment({
              uuid: "inst-pay",
              installment_number: 1,
              amount: "500.00",
              due_date: dueDate,
              status: "PENDING",
            }),
          ],
          count: 1,
        }),
      ),
      http.post(
        "*/api/v1/finances/installments/:uuid/mark-as-paid/",
        () =>
          HttpResponse.json(
            createMockInstallment({
              uuid: "inst-pay",
              status: "PAID",
            }),
          ),
      ),
    );

    render(<WeddingUpcomingInstallments weddingUuid={WEDDING_UUID} />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /pagar/i }),
      ).toBeInTheDocument();
    });

    const user = (await import("@/test-utils")).userEvent;
    await user.setup().click(screen.getByRole("button", { name: /pagar/i }));

    await waitFor(() => {
      expect(toastSuccess).toHaveBeenCalledWith(
        "Parcela marcada como paga!",
      );
    });
  });

  it("shows error toast when mark-as-paid fails", async () => {
    const { http, HttpResponse } = await import("msw");
    const dueDate = futureDate(10);

    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({
          items: [
            createMockInstallment({
              uuid: "inst-fail",
              installment_number: 1,
              amount: "500.00",
              due_date: dueDate,
              status: "PENDING",
            }),
          ],
          count: 1,
        }),
      ),
      http.post(
        "*/api/v1/finances/installments/:uuid/mark-as-paid/",
        () =>
          HttpResponse.json(
            { detail: "Erro ao processar pagamento." },
            { status: 400 },
          ),
      ),
    );

    render(<WeddingUpcomingInstallments weddingUuid={WEDDING_UUID} />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /pagar/i }),
      ).toBeInTheDocument();
    });

    const user = (await import("@/test-utils")).userEvent;
    await user.setup().click(screen.getByRole("button", { name: /pagar/i }));

    await waitFor(() => {
      expect(toastError).toHaveBeenCalledWith(
        "Erro ao processar pagamento.",
      );
    });
  });

  it("disables pagar button while payment is in progress", async () => {
    const { http, HttpResponse } = await import("msw");
    const dueDate = futureDate(10);

    let resolvePayment!: (value: unknown) => void;
    const paymentPromise = new Promise((resolve) => {
      resolvePayment = resolve;
    });

    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({
          items: [
            createMockInstallment({
              uuid: "inst-loading",
              installment_number: 1,
              amount: "500.00",
              due_date: dueDate,
              status: "PENDING",
            }),
          ],
          count: 1,
        }),
      ),
      http.post(
        "*/api/v1/finances/installments/:uuid/mark-as-paid/",
        async () => {
          await paymentPromise;
          return HttpResponse.json(
            createMockInstallment({ uuid: "inst-loading", status: "PAID" }),
          );
        },
      ),
    );

    render(<WeddingUpcomingInstallments weddingUuid={WEDDING_UUID} />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /pagar/i }),
      ).toBeInTheDocument();
    });

    const user = (await import("@/test-utils")).userEvent;
    const clickPromise = user
      .setup()
      .click(screen.getByRole("button", { name: /pagar/i }));

    // The button should be disabled immediately after click (before MSW resolves)
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /pagar/i }),
      ).toBeDisabled();
    });

    // Resolve the payment so the test can finish cleanly
    resolvePayment(null);
    await clickPromise;
  });

  it("renders card description", async () => {
    const { http, HttpResponse } = await import("msw");

    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({
          items: [
            createMockInstallment({
              uuid: "inst-desc",
              installment_number: 1,
              status: "PENDING",
            }),
          ],
          count: 1,
        }),
      ),
    );

    render(<WeddingUpcomingInstallments weddingUuid={WEDDING_UUID} />);

    await waitFor(() => {
      expect(
        screen.getByText(/Compromissos financeiros agendados/i),
      ).toBeInTheDocument();
    });
  });
});
