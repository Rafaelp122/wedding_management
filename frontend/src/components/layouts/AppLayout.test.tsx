import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@/test-utils";
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

vi.mock("@/components/ui/dropdown-menu", () => ({
  DropdownMenu: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  DropdownMenuTrigger: ({ children, asChild }: { children: React.ReactNode; asChild?: boolean }) =>
    asChild ? <>{children}</> : <button>{children}</button>,
  DropdownMenuContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  DropdownMenuLabel: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  DropdownMenuSeparator: () => <hr />,
  DropdownMenuItem: ({ children, asChild }: { children: React.ReactNode; asChild?: boolean }) =>
    asChild ? <>{children}</> : <div>{children}</div>,
}));
vi.mock("@/hooks/useDocumentTitle", () => ({
  useDocumentTitle: vi.fn(),
}));

vi.mock("@/api/generated/v1/endpoints/weddings/weddings", () => ({
  useWeddingsRead: vi.fn(() => ({
    data: undefined,
    isLoading: false,
  })),
  useWeddingsList: vi.fn(() => ({
    data: { data: { items: [], count: 0 } },
    isLoading: false,
  })),
}));

import { useWeddingsRead, useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";

describe("AppLayout", () => {
  it("renders the page title for dashboard path", () => {
    render(<AppLayout />, { initialEntries: ["/dashboard"] });
    expect(screen.getByText("Dashboard Geral")).toBeInTheDocument();
  });

  it("renders notification bell with correct aria-label", () => {
    render(<AppLayout />, { initialEntries: ["/dashboard"] });
    expect(screen.getByRole("button", { name: /notificações/i })).toBeInTheDocument();
  });

  it("renders notification dropdown with empty state message", () => {
    render(<AppLayout />, { initialEntries: ["/dashboard"] });
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

  it("renders wedding detail title for wedding paths if not loaded yet", () => {
    render(<AppLayout />, { initialEntries: ["/weddings/abc-123"] });
    expect(screen.getByText("Detalhes do Casamento")).toBeInTheDocument();
  });

  it("renders supplier detail title for supplier paths", () => {
    render(<AppLayout />, { initialEntries: ["/suppliers/abc-123"] });
    expect(screen.getByText("Detalhes do Fornecedor")).toBeInTheDocument();
  });

  it("renders fallback title for unknown paths", () => {
    render(<AppLayout />, { initialEntries: ["/unknown"] });
    expect(screen.getByText("Painel de Controle")).toBeInTheDocument();
  });

  it("renders dynamic breadcrumbs and status badge when wedding details are loaded", () => {
    vi.mocked(useWeddingsRead).mockReturnValue({
      data: {
        data: {
          uuid: "abc-123",
          groom_name: "Júlia",
          bride_name: "Marcos",
          status: "IN_PROGRESS",
          date: "2026-09-20",
          location: "Fazenda Vila Rica, SP",
          expected_guests: 250,
          created_at: "",
          updated_at: "",
        },
      },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsRead>);

    vi.mocked(useWeddingsList).mockReturnValue({
      data: {
        data: {
          items: [
            { uuid: "abc-123", groom_name: "Júlia", bride_name: "Marcos", status: "IN_PROGRESS", date: "2026-09-20", location: "Fazenda Vila Rica, SP", expected_guests: 250, created_at: "", updated_at: "" },
            { uuid: "xyz-789", groom_name: "Outro", bride_name: "Casal", status: "IN_PROGRESS", date: "2026-09-20", location: "Outro Local", expected_guests: 150, created_at: "", updated_at: "" },
          ],
          count: 2,
        },
      },
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useWeddingsList>);

    render(<AppLayout />, { initialEntries: ["/weddings/abc-123"] });
    expect(screen.getByText("Casamentos")).toBeInTheDocument();
    expect(screen.getAllByText(/Júlia & Marcos/i).length).toBeGreaterThan(0);
  });
});
