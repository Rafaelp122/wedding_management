
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { AppLayout } from "@/components/layouts/AppLayout";

vi.mock("@/components/ui/sidebar", () => ({
  SidebarProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  SidebarInset: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div className={className}>{children}</div>
  ),
  SidebarTrigger: ({ className }: { className?: string }) => (
    <button className={className}>Toggle</button>
  ),
}));

vi.mock("@/components/ui/separator", () => ({
  Separator: ({ orientation, className }: { orientation?: string; className?: string }) => (
    <hr data-orientation={orientation} className={className} />
  ),
}));

vi.mock("../app-sidebar", () => ({
  AppSidebar: () => null,
}));


vi.mock("@/hooks/useDocumentTitle", () => ({
  useDocumentTitle: vi.fn(),
}));

import { server } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { getWeddingsListMockHandler } from "@/api/generated/v1/endpoints/weddings/weddings.msw";

describe("AppLayout", () => {
  beforeEach(() => {
    server.use(
      http.get("*/api/v1/weddings/:uuid/", () => {
        return new HttpResponse(null, { status: 404 });
      }),
      getWeddingsListMockHandler({
        items: [],
        count: 0
      })
    );
  });
  it("renders the page title for dashboard path", () => {
    render(<AppLayout />, { initialEntries: ["/dashboard"] });
    expect(screen.getByText("Dashboard Geral")).toBeInTheDocument();
  });

  it("renders notification bell with correct aria-label", () => {
    render(<AppLayout />, { initialEntries: ["/dashboard"] });
    expect(screen.getByRole("button", { name: /notificações/i })).toBeInTheDocument();
  });

  it("renders notification dropdown with empty state message", async () => {
    const user = userEvent.setup();
    render(<AppLayout />, { initialEntries: ["/dashboard"] });
    const bellButton = screen.getByRole("button", { name: /notificações/i });
    await user.click(bellButton);
    expect(screen.getByText("Notificações")).toBeInTheDocument();
    expect(
      screen.getByText("Você não tem novas notificações no momento."),
    ).toBeInTheDocument();
  });

  it("does not render a static red badge", () => {
    render(<AppLayout />, { initialEntries: ["/dashboard"] });
    const bellButton = screen.getByRole("button", { name: /notificações/i });
    expect(bellButton.querySelector(".bg-destructive")).not.toBeInTheDocument();
  });

  it("renders wedding detail title for wedding paths if not loaded yet", async () => {
    render(<AppLayout />, { initialEntries: ["/weddings/abc-123"] });
    expect(await screen.findByText("Detalhes do Casamento")).toBeInTheDocument();
  });

  it("renders supplier detail title for supplier paths", () => {
    render(<AppLayout />, { initialEntries: ["/suppliers/abc-123"] });
    expect(screen.getByText("Detalhes do Fornecedor")).toBeInTheDocument();
  });

  it("renders fallback title for unknown paths", () => {
    render(<AppLayout />, { initialEntries: ["/unknown"] });
    expect(screen.getByText("Painel de Controle")).toBeInTheDocument();
  });

  it("renders dynamic breadcrumbs and status badge when wedding details are loaded", async () => {
    server.use(
      http.get("*/api/v1/weddings/abc-123/", () => {
        return HttpResponse.json({
          uuid: "abc-123",
          groom_name: "Júlia",
          bride_name: "Marcos",
          status: "IN_PROGRESS",
          date: "2026-09-20",
          location: "Fazenda Vila Rica, SP",
          expected_guests: 250,
          created_at: "",
          updated_at: "",
        });
      }),
      getWeddingsListMockHandler({
        items: [
          { uuid: "abc-123", groom_name: "Júlia", bride_name: "Marcos", status: "IN_PROGRESS", date: "2026-09-20", location: "Fazenda Vila Rica, SP", expected_guests: 250, created_at: "", updated_at: "", template: null },
          { uuid: "xyz-789", groom_name: "Outro", bride_name: "Casal", status: "IN_PROGRESS", date: "2026-09-20", location: "Outro Local", expected_guests: 150, created_at: "", updated_at: "", template: null },
        ],
        count: 2,
      })
    );

    render(<AppLayout />, { initialEntries: ["/weddings/abc-123"] });
    expect(await screen.findByText("Casamentos")).toBeInTheDocument();
    expect((await screen.findAllByText(/Júlia & Marcos/i)).length).toBeGreaterThan(0);
  });
});
