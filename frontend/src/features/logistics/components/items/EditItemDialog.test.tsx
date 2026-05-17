import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { EditItemDialog } from "./EditItemDialog";
import { createMockItem } from "@/test-data";

// Polyfills for Radix UI Select in jsdom (missing browser APIs)
beforeAll(() => {
  Element.prototype.hasPointerCapture ??= () => false;
  Element.prototype.setPointerCapture ??= () => {};
  Element.prototype.releasePointerCapture ??= () => {};
  Element.prototype.scrollIntoView ??= () => {};
});

// ============================================================================
// Hoisted mocks – available at module scope before vi.mock factories run
// ============================================================================

const { toastSuccess, toastError } = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: {
      ...actual.toast,
      success: toastSuccess,
      error: toastError,
    },
  };
});

const mockMutate = vi.hoisted(
  () => vi.fn((_variables, options) => options?.onSuccess?.(null)),
);

const mockContractsList = vi.hoisted(() => vi.fn());

vi.mock(
  "@/api/generated/v1/endpoints/logistics/logistics",
  async () => ({
    useLogisticsItemsUpdate: () => ({
      mutate: mockMutate,
      isPending: false,
    }),
    useLogisticsContractsList: () => mockContractsList(),
  }),
);

// ============================================================================
// Helpers
// ============================================================================

function mockQueryResponse(data: unknown) {
  return { data, isLoading: false, isError: false, error: null };
}

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

// ============================================================================
// Tests
// ============================================================================

describe("EditItemDialog", () => {
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockContractsList.mockReturnValue(
      mockQueryResponse({ data: { items: [], count: 0 } }),
    );
  });

  // -----------------------------------------------------------------------
  // 1. Renders form with pre-filled data
  // -----------------------------------------------------------------------
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

    // Dialog title and description
    expect(screen.getByText("Editar Item")).toBeInTheDocument();
    expect(
      screen.getByText("Altere as informações do item logístico."),
    ).toBeInTheDocument();

    // Pre-filled name input
    expect(screen.getByLabelText("Nome")).toHaveValue("Cadeiras Tiffany");

    // Pre-filled description
    expect(screen.getByLabelText("Descrição")).toHaveValue(
      "Cadeiras decorativas para cerimônia",
    );

    // Pre-filled quantity (number input)
    const quantityInput = screen.getByRole("spinbutton", {
      name: /quantidade/i,
    });
    expect(quantityInput).toHaveValue(150);

    // Selects rendered
    expect(
      screen.getByRole("combobox", { name: /status/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("combobox", { name: /contrato/i }),
    ).toBeInTheDocument();

    // Submit button
    expect(
      screen.getByRole("button", { name: /salvar/i }),
    ).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 2. Submits only changed fields
  // -----------------------------------------------------------------------
  it("submits only changed fields", async () => {
    const user = userEvent.setup();
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

    // Change the name field
    const nameInput = screen.getByLabelText("Nome");
    await user.clear(nameInput);
    await user.type(nameInput, "Cadeiras Tiffany Plus");

    // Submit
    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith(
        { uuid: "item-1", data: { name: "Cadeiras Tiffany Plus" } },
        expect.any(Object),
      );
    });
  });

  // -----------------------------------------------------------------------
  // 3. Ignores submit when nothing changed
  // -----------------------------------------------------------------------
  it("ignores submit when nothing changed", async () => {
    const user = userEvent.setup();
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

    // Click submit without making any changes
    await user.click(screen.getByRole("button", { name: /salvar/i }));

    // mutate should NOT have been called
    expect(mockMutate).not.toHaveBeenCalled();

    // Dialog should have been closed via the empty-payload guard
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  // -----------------------------------------------------------------------
  // 4. Shows success toast on successful submit
  // -----------------------------------------------------------------------
  it("shows success toast on successful submit", async () => {
    const user = userEvent.setup();
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

    // Change the name
    const nameInput = screen.getByLabelText("Nome");
    await user.clear(nameInput);
    await user.type(nameInput, "Cadeiras Reformuladas");

    // Submit
    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(toastSuccess).toHaveBeenCalledWith(
        "Item atualizado com sucesso!",
      );
    });

    // onSuccess callback from props should have been called
    expect(onSuccess).toHaveBeenCalled();
  });
});
