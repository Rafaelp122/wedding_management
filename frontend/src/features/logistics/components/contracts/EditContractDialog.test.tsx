import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor, server } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { EditContractDialog } from "./EditContractDialog";
import { createMockContract, createMockSupplier } from "@/test-data";
import { toast } from "sonner";

beforeAll(() => {
  Element.prototype.hasPointerCapture ??= () => false;
  Element.prototype.setPointerCapture ??= () => {};
  Element.prototype.releasePointerCapture ??= () => {};
  Element.prototype.scrollIntoView ??= () => {};
});

const mockSupplier = createMockSupplier({
  uuid: "supplier-uuid-123",
  name: "Buffet Gourmet Ltda",
});

const weddingUuid = "test-wedding-uuid";

function createMockContractWithName(overrides: Partial<Record<string, unknown>> = {}) {
  return createMockContract({
    uuid: "contract-1",
    name: "Buffet Casamento",
    supplier: "supplier-uuid-123",
    total_amount: "5000.00",
    status: "SIGNED",
    description: "Buffet para 150 convidados",
    ...overrides,
  });
}

describe("EditContractDialog", () => {
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    server.use(
      http.get("*/api/v1/logistics/suppliers/", () =>
        HttpResponse.json({ items: [mockSupplier], count: 1 }),
      ),
      http.get("*/api/v1/logistics/contracts/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
    );
  });

  it("renders form with pre-filled data", () => {
    const contract = createMockContractWithName();

    render(
      <EditContractDialog
        contract={contract}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.getByText("Editar Contrato")).toBeInTheDocument();
    expect(
      screen.getByText("Altere os metadados do contrato de fornecedor."),
    ).toBeInTheDocument();

    expect(screen.getByLabelText("Nome do Contrato")).toHaveValue(
      "Buffet Casamento",
    );

    expect(screen.getByLabelText("Descrição")).toHaveValue(
      "Buffet para 150 convidados",
    );

    const amountInput = screen.getByRole("spinbutton", {
      name: /valor total/i,
    });
    expect(amountInput).toHaveValue(5000);

    expect(
      screen.getByRole("combobox", { name: /fornecedor/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("combobox", { name: /status/i }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: /salvar/i }),
    ).toBeInTheDocument();
  });

  it("submits only changed fields", async () => {
    const user = userEvent.setup();
    const contract = createMockContractWithName();

    let capturedBody: unknown;
    server.use(
      http.patch("*/api/v1/logistics/contracts/:uuid/", async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json(createMockContract({ uuid: "contract-1" }));
      }),
    );

    render(
      <EditContractDialog
        contract={contract}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const nameInput = screen.getByLabelText("Nome do Contrato");
    await user.clear(nameInput);
    await user.type(nameInput, "Buffet VIP Atualizado");

    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(capturedBody).toMatchObject({ name: "Buffet VIP Atualizado" });
    });
  });

  it("ignores submit when nothing changed", async () => {
    const user = userEvent.setup();
    const contract = createMockContractWithName();

    const patchSpy = vi.fn();
    server.use(
      http.patch("*/api/v1/logistics/contracts/:uuid/", (info) => {
        patchSpy(info);
        return HttpResponse.json(createMockContract());
      }),
    );

    render(
      <EditContractDialog
        contract={contract}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await user.click(screen.getByRole("button", { name: /salvar/i }));

    expect(patchSpy).not.toHaveBeenCalled();
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("shows success toast on successful submit", async () => {
    const user = userEvent.setup();
    const contract = createMockContractWithName();

    server.use(
      http.patch("*/api/v1/logistics/contracts/:uuid/", async ({ request }) => {
        await request.json();
        return HttpResponse.json(createMockContract({ uuid: "contract-1" }));
      }),
    );

    render(
      <EditContractDialog
        contract={contract}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const nameInput = screen.getByLabelText("Nome do Contrato");
    await user.clear(nameInput);
    await user.type(nameInput, "Nome Alterado");

    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Contrato atualizado com sucesso!",
      );
    });

    expect(onSuccess).toHaveBeenCalled();
  });
});
