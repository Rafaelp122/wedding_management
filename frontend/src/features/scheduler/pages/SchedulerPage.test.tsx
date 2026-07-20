import { describe, expect, it } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import SchedulerPage from "@/features/scheduler/pages/SchedulerPage";
import { server } from "@/mocks/server";
import { createMockEvent, createMockWedding } from "@/test-data";
import { HttpResponse, http } from "msw";
import { toast } from "sonner";

describe("SchedulerPage", () => {
  it("shows loading state initially", () => {
    render(<SchedulerPage />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders header after loading", async () => {
    render(<SchedulerPage />);

    await waitFor(() => {
      expect(screen.getByText("Scheduler")).toBeInTheDocument();
    });
  });

  it("shows new event button after loading", async () => {
    render(<SchedulerPage />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /novo evento/i }),
      ).toBeInTheDocument();
    });
  });

  it("shows pagination in table view after loading", async () => {
    render(<SchedulerPage />);

    await waitFor(() => {
      const prevButton = screen.getByRole("button", { name: "Anterior" });
      const nextButton = screen.getByRole("button", { name: "Próximo" });
      expect(prevButton).toBeInTheDocument();
      expect(nextButton).toBeInTheDocument();
    });
  });

  it("allows toggling to calendar view", async () => {
    render(<SchedulerPage />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /tabela/i }),
      ).toBeInTheDocument();
    });

    const user = userEvent.setup();
    // O botão Calendário é o próximo elemento irmão (ou podemos buscar por papel botão)
    const buttons = screen.getAllByRole("button");
    const calBtn = buttons.find((btn) => btn.textContent?.includes("Calendário"));

    if (calBtn) {
      await user.click(calBtn);
      await waitFor(() => {
        expect(screen.getByText("Hoje")).toBeInTheDocument();
      });
    }
  });

  it("shows the API error state", async () => {
    server.use(
      http.get("*/api/v1/scheduler/events/", () =>
        HttpResponse.json({ detail: "Falha" }, { status: 500 }),
      ),
    );

    render(<SchedulerPage />);

    expect(await screen.findByText("Erro ao carregar scheduler")).toBeInTheDocument();
  });

  it("blocks creation when there are no weddings", async () => {
    server.use(
      http.get("*/api/v1/scheduler/events/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
    );
    const user = userEvent.setup();
    render(<SchedulerPage />);

    await user.click(await screen.findByRole("button", { name: /novo evento/i }));
    expect(toast.warning).toHaveBeenCalled();
    expect(screen.queryByText("Novo Evento", { selector: "h2" })).not.toBeInTheDocument();
  });

  it("opens create and edit dialogs from page actions", async () => {
    const event = createMockEvent({
      title: "Evento selecionavel",
      start_time: new Date().toISOString(),
    });
    server.use(
      http.get("*/api/v1/scheduler/events/", () =>
        HttpResponse.json({ items: [event], count: 1 }),
      ),
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({ items: [createMockWedding()], count: 1 }),
      ),
    );
    const user = userEvent.setup();
    render(<SchedulerPage />);

    await user.click(await screen.findByRole("button", { name: /novo evento/i }));
    expect(screen.getByRole("heading", { name: "Novo Evento" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Cancelar" }));

    await user.click(screen.getByRole("button", { name: /calendário/i }));
    await user.click(await screen.findByText(/Evento selecionavel/));
    expect(screen.getByRole("heading", { name: "Editar Evento" })).toBeInTheDocument();
  });
});
