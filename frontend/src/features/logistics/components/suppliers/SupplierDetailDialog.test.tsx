
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@/test-utils";
import { SupplierDetailDialog } from "@/features/logistics/components/suppliers/SupplierDetailDialog";
import { createMockSupplier } from "@/test-data";
import { http, HttpResponse } from "msw";
import { server } from "@/mocks/server";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const defaultProps = {
  supplierUuid: "s-1",
  open: true,
  onOpenChange: vi.fn(),
} as const;

const baseSupplier = createMockSupplier({
  uuid: "s-1",
  name: "Buffet Gourmet",
  email: "buffet@email.com",
  phone: "(11) 99999-0000",
  cnpj: "12.345.678/0001-90",
  is_active: true,
  created_at: "2025-01-01T00:00:00Z",
  updated_at: "2025-01-15T10:30:00Z",
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("SupplierDetailDialog", () => {
  // ── Loading state ──────────────────────────────────────────────────────

  it("shows loading skeleton when data is loading", () => {
    server.use(
      http.get("*/api/v1/logistics/suppliers/:uuid/", () => {
        return new Promise(() => {}); // never resolve
      }),
    );

    render(<SupplierDetailDialog {...defaultProps} />);

    // Skeleton divs use the animate-pulse class — verify at least one is rendered
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThanOrEqual(4);

    // No error / no supplier content should appear while loading
    expect(
      screen.queryByText("Não foi possível carregar os dados do fornecedor."),
    ).not.toBeInTheDocument();
    expect(screen.queryByText("Fornecedor não encontrado.")).not.toBeInTheDocument();
    expect(screen.queryByText("Buffet Gourmet")).not.toBeInTheDocument();
  });

  // ── Error state ────────────────────────────────────────────────────────

  it("shows error alert when query fails", async () => {
    server.use(
      http.get("*/api/v1/logistics/suppliers/:uuid/", () => {
        return new HttpResponse(null, { status: 500 });
      }),
    );

    render(<SupplierDetailDialog {...defaultProps} />);

    expect(
      await screen.findByText("Não foi possível carregar os dados do fornecedor."),
    ).toBeInTheDocument();

    // Alert should use the destructive variant
    const alert = screen
      .getByText("Não foi possível carregar os dados do fornecedor.")
      .closest('[role="alert"]');
    expect(alert).toBeInTheDocument();
  });

  // ── Not-found state ────────────────────────────────────────────────────

  it("shows not-found message when supplier is null", async () => {
    server.use(
      http.get("*/api/v1/logistics/suppliers/:uuid/", () => {
        return HttpResponse.json(null);
      }),
    );

    render(<SupplierDetailDialog {...defaultProps} />);

    expect(await screen.findByText("Fornecedor não encontrado.")).toBeInTheDocument();
  });

  // ── Success state ──────────────────────────────────────────────────────

  it("renders supplier name, status badge, email, phone, WhatsApp link and CNPJ", async () => {
    server.use(
      http.get("*/api/v1/logistics/suppliers/:uuid/", () => {
        return HttpResponse.json(baseSupplier);
      }),
    );

    render(<SupplierDetailDialog {...defaultProps} />);

    // Title
    expect(await screen.findByText("Buffet Gourmet")).toBeInTheDocument();

    // Status badge
    expect(screen.getByText("Ativo")).toBeInTheDocument();

    // Email
    expect(screen.getByText("buffet@email.com")).toBeInTheDocument();

    // Phone
    expect(screen.getByText("(11) 99999-0000")).toBeInTheDocument();

    // WhatsApp icon
    const waLink = screen.getByTitle("Abrir WhatsApp");
    expect(waLink).toBeInTheDocument();

    // CNPJ
    expect(screen.getByText("CNPJ: 12.345.678/0001-90")).toBeInTheDocument();

    // Dates
    expect(screen.getByText(/Cadastrado em:/)).toBeInTheDocument();
    expect(screen.getByText(/Atualizado em:/)).toBeInTheDocument();
  });

  // ── WhatsApp link ──────────────────────────────────────────────────────

  it("WhatsApp link has correct href with country code +55", async () => {
    server.use(
      http.get("*/api/v1/logistics/suppliers/:uuid/", () => {
        return HttpResponse.json(baseSupplier);
      }),
    );

    render(<SupplierDetailDialog {...defaultProps} />);

    const waLink = await screen.findByTitle("Abrir WhatsApp");

    // Digits-only phone: (11) 99999-0000 → 11999990000
    // Component prepends 55 → https://wa.me/5511999990000
    expect(waLink).toHaveAttribute(
      "href",
      "https://wa.me/5511999990000",
    );
  });

  // ── Email link ─────────────────────────────────────────────────────────

  it("email link has mailto href", async () => {
    server.use(
      http.get("*/api/v1/logistics/suppliers/:uuid/", () => {
        return HttpResponse.json(baseSupplier);
      }),
    );

    render(<SupplierDetailDialog {...defaultProps} />);

    const emailLink = (await screen.findByText("buffet@email.com")).closest("a");
    expect(emailLink).toHaveAttribute("href", "mailto:buffet@email.com");
  });

  // ── Inactive supplier badge ────────────────────────────────────────────

  it("shows Inativo badge when supplier is inactive", async () => {
    const inactive = createMockSupplier({ is_active: false, name: "Fotógrafo Arte" });

    server.use(
      http.get("*/api/v1/logistics/suppliers/:uuid/", () => {
        return HttpResponse.json(inactive);
      }),
    );

    render(
      <SupplierDetailDialog
        supplierUuid="s-2"
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(await screen.findByText("Inativo")).toBeInTheDocument();
    expect(screen.queryByText("Ativo")).not.toBeInTheDocument();
  });

  // ── Hides updated_at when same as created_at ───────────────────────────

  it("hides 'Atualizado em' when updated_at equals created_at", async () => {
    const sameDates = createMockSupplier({
      created_at: "2025-01-01T00:00:00Z",
      updated_at: "2025-01-01T00:00:00Z",
    });

    server.use(
      http.get("*/api/v1/logistics/suppliers/:uuid/", () => {
        return HttpResponse.json(sameDates);
      }),
    );

    render(<SupplierDetailDialog {...defaultProps} />);

    expect(await screen.findByText(/Cadastrado em:/)).toBeInTheDocument();
    expect(screen.queryByText(/Atualizado em:/)).not.toBeInTheDocument();
  });
});
