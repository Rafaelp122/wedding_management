import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor, server } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { EditItemDialog } from "./EditItemDialog";
import { createMockItem } from "@/test-data";
import { toast } from "sonner";

beforeAll(() => {
  Element.prototype.hasPointerCapture ??= () => false;
  Element.prototype.setPointerCapture ??= () => {};
  Element.prototype.releasePointerCapture ??= () => {};
  Element.prototype.scrollIntoView ??= () => {};
});

const weddingUuid = "test-wedding-uuid";

function createMockItemWithDefaults(
  overrides: Partial<Record<string, unknown>> = {},
) {
  return createMockItem({
    uuid: "item-1",
    name: "Cadeiras Tiffany",
    description: "Cadeiras decorativas para cerimônia",
    quantity: 150,
    acquisition_status: "PENDING",
    ...overrides,
  });
}

describe("EditItemDialog", () => {
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    server.use(
      http.get("*/api/v1/logistics/contracts/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
    );
  });

  it("renders form with pre-filled data", () => {
    const item = createMockItemWithDefaults();

    render(
      <EditItemDialog
        item={item}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.getByText("Editar Item")).toBeInTheDocument();
    expect(
      screen.getByText("Altere as informações do item logístico."),
    ).toBeInTheDocument();

    expect(screen.getByLabelText("Nome")).toHaveValue("Cadeiras Tiffany");

    expect(screen.getByLabelText("Descrição")).toHaveValue(
      "Cadeiras decorativas para cerimônia",
    );

    const quantityInput = screen.getByRole("spinbutton", {
      name: /quantidade/i,
    });
    expect(quantityInput).toHaveValue(150);

    expect(
      screen.getByRole("combobox", { name: /status/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("combobox", { name: /contrato/i }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: /salvar/i }),
    ).toBeInTheDocument();
  });

  it("submits only changed fields", async () => {
    const user = userEvent.setup();
    const item = createMockItemWithDefaults();

    let capturedBody: unknown;
    server.use(
      http.patch("*/api/v1/logistics/items/:uuid/", async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json(createMockItem({ uuid: "item-1" }));
      }),
    );

    render(
      <EditItemDialog
        item={item}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const nameInput = screen.getByLabelText("Nome");
    await user.clear(nameInput);
    await user.type(nameInput, "Cadeiras Tiffany Plus");

    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(capturedBody).toMatchObject({ name: "Cadeiras Tiffany Plus" });
    });
  });

  it("ignores submit when nothing changed", async () => {
    const user = userEvent.setup();
    const item = createMockItemWithDefaults();

    const patchSpy = vi.fn();
    server.use(
      http.patch("*/api/v1/logistics/items/:uuid/", (info) => {
        patchSpy(info);
        return HttpResponse.json(createMockItem());
      }),
    );

    render(
      <EditItemDialog
        item={item}
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
    const item = createMockItemWithDefaults();

    server.use(
      http.patch("*/api/v1/logistics/items/:uuid/", async ({ request }) => {
        await request.json();
        return HttpResponse.json(createMockItem({ uuid: "item-1" }));
      }),
    );

    render(
      <EditItemDialog
        item={item}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const nameInput = screen.getByLabelText("Nome");
    await user.clear(nameInput);
    await user.type(nameInput, "Cadeiras Reformuladas");

    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Item atualizado com sucesso!",
      );
    });

    expect(onSuccess).toHaveBeenCalled();
  });
});
