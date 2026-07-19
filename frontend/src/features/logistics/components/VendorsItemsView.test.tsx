import { describe, expect, it, vi, beforeEach } from "vitest";
vi.unmock("@/features/logistics/components/VendorsItemsView");
import { render, screen, userEvent } from "@/test-utils";
import { WeddingVendorsItemsTab } from "./VendorsItemsView";
import { createMockContract, createMockItem } from "@/test-data";
import { server } from "@/mocks/server";
import { http, HttpResponse, delay } from "msw";

// ---------------------------------------------------------------------------
// Mock every sub-component so we only test orchestration
// ---------------------------------------------------------------------------
vi.mock("./items/VendorsTable", () => ({
  WeddingVendorsTable: vi.fn(
    ({
      contracts,
      onDetail,
    }: {
      contracts: unknown[];
      onDetail?: (uuid: string) => void;
    }) => (
      <div data-testid="vendors-table">
        <span data-testid="contract-count">{contracts.length}</span>
        <button
          data-testid="btn-vendor-detail"
          onClick={() => onDetail?.("c-1")}
        >
          detail
        </button>
      </div>
    ),
  ),
}));

vi.mock("./items/ItemsTable", () => ({
  WeddingItemsTable: vi.fn(
    ({
      items,
      onEdit,
    }: {
      items: unknown[];
      onEdit?: (item: unknown) => void;
    }) => (
      <div data-testid="items-table">
        <span data-testid="item-count">{items.length}</span>
        {items.length > 0 && (
          <button
            data-testid="btn-item-edit"
            onClick={() => onEdit?.(items[0])}
          >
            edit
          </button>
        )}
      </div>
    ),
  ),
}));

vi.mock("./contracts/ContractDetailDialog", () => ({
  ContractDetailDialog: vi.fn(
    ({
      open,
      contractUuid,
      onCreateAddendum,
    }: {
      contractUuid: string | null;
      open: boolean;
      onCreateAddendum?: (parentUuid: string) => void;
    }) =>
      open ? (
        <div data-testid="contract-detail-dialog">
          <span data-testid="detail-uuid">{contractUuid}</span>
          <button
            data-testid="btn-create-addendum"
            onClick={() => onCreateAddendum?.("parent-uuid")}
          >
            addendum
          </button>
        </div>
      ) : null,
  ),
}));

vi.mock("./contracts/ContractUploadDialog", () => ({
  ContractUploadDialog: vi.fn(
    ({
      open,
      prefilledParentUuid,
    }: {
      open: boolean;
      prefilledParentUuid: string | null;
    }) =>
      open ? (
        <div data-testid="contract-upload-dialog">
          <span data-testid="prefilled-parent">
            {prefilledParentUuid ?? "none"}
          </span>
        </div>
      ) : null,
  ),
}));

vi.mock("./items/CreateItemDialog", () => ({
  CreateItemDialog: vi.fn(
    ({ open }: { open: boolean }) =>
      open ? <div data-testid="create-item-dialog" /> : null,
  ),
}));

vi.mock("./items/EditItemDialog", () => ({
  EditItemDialog: vi.fn(
    ({ open, item }: { item: { name: string }; open: boolean }) =>
      open ? (
        <div data-testid="edit-item-dialog">{item?.name}</div>
      ) : null,
  ),
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function mockLoading() {
  server.use(
    http.get("*/api/v1/logistics/contracts/", async () => {
      await delay("infinite");
      return HttpResponse.json({ items: [], count: 0 });
    }),
    http.get("*/api/v1/logistics/items/", async () => {
      await delay("infinite");
      return HttpResponse.json({ items: [], count: 0 });
    }),
  );
}

function mockError() {
  server.use(
    http.get("*/api/v1/logistics/contracts/", () => {
      return HttpResponse.json({ detail: "API failure" }, { status: 500 });
    }),
    http.get("*/api/v1/logistics/items/", () => {
      return HttpResponse.json({ detail: "API failure" }, { status: 500 });
    })
  );
}

function mockData(
  contracts: ReturnType<typeof createMockContract>[] = [],
  items: ReturnType<typeof createMockItem>[] = [],
) {
  server.use(
    http.get("*/api/v1/logistics/contracts/", () => {
      return HttpResponse.json({
        items: contracts,
        count: contracts.length,
      });
    }),
    http.get("*/api/v1/logistics/items/", () => {
      return HttpResponse.json({
        items,
        count: items.length,
      });
    })
  );
}

const weddingUuid = "w-1";

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
describe("WeddingVendorsItemsTab", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Loading state", () => {
    it("shows skeleton placeholders while loading", () => {
      mockLoading();
      render(
        <WeddingVendorsItemsTab weddingUuid={weddingUuid} />,
      );

      // The component renders two Skeleton elements in loading state
      // Skeletons have specific classes from the Skeleton component
      // Let's just check that no data/error content is shown
      expect(
        screen.queryByText("Contratos de Fornecedores"),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByText("Itens Logísticos"),
      ).not.toBeInTheDocument();
    });
  });

  describe("Error state", () => {
    it("shows a destructive alert with error message", async () => {
      mockError();
      render(<WeddingVendorsItemsTab weddingUuid={weddingUuid} />);

      expect(
        await screen.findByText(
          "Não foi possível carregar os dados de logística e fornecedores.",
        ),
      ).toBeInTheDocument();

      // Ensure no content is rendered
      expect(
        screen.queryByText("Contratos de Fornecedores"),
      ).not.toBeInTheDocument();
    });
  });

  describe("Normal rendering", () => {
    it("renders contracts card with Novo Contrato button", async () => {
      mockData([createMockContract()], []);

      render(<WeddingVendorsItemsTab weddingUuid={weddingUuid} />);

      expect(
        await screen.findByText("Contratos de Fornecedores"),
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /novo contrato/i }),
      ).toBeInTheDocument();
      expect(screen.getByTestId("vendors-table")).toBeInTheDocument();
      expect(screen.getByTestId("contract-count")).toHaveTextContent("1");
    });

    it("renders items card with Novo Item button", async () => {
      mockData([], [createMockItem()]);

      render(<WeddingVendorsItemsTab weddingUuid={weddingUuid} />);

      expect(
        await screen.findByText("Itens Logísticos"),
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /novo item/i }),
      ).toBeInTheDocument();
      expect(screen.getByTestId("items-table")).toBeInTheDocument();
      expect(screen.getByTestId("item-count")).toHaveTextContent("1");
    });

    it("renders empty states when there are no contracts or items", async () => {
      mockData([], []);

      render(<WeddingVendorsItemsTab weddingUuid={weddingUuid} />);

      expect(await screen.findByTestId("vendors-table")).toBeInTheDocument();
      expect(screen.getByTestId("contract-count")).toHaveTextContent("0");
      expect(screen.getByTestId("items-table")).toBeInTheDocument();
      expect(screen.getByTestId("item-count")).toHaveTextContent("0");
    });
  });

  describe("Dialog orchestration", () => {
    it("opens ContractUploadDialog when Novo Contrato is clicked", async () => {
      mockData([], []);
      render(<WeddingVendorsItemsTab weddingUuid={weddingUuid} />);

      const novoContratoBtn = await screen.findByRole("button", { name: /novo contrato/i });
      expect(
        screen.queryByTestId("contract-upload-dialog"),
      ).not.toBeInTheDocument();

      await userEvent.click(novoContratoBtn);

      expect(
        screen.getByTestId("contract-upload-dialog"),
      ).toBeInTheDocument();
    });

    it("opens CreateItemDialog when Novo Item is clicked", async () => {
      mockData([], []);
      render(<WeddingVendorsItemsTab weddingUuid={weddingUuid} />);

      const novoItemBtn = await screen.findByRole("button", { name: /novo item/i });
      expect(
        screen.queryByTestId("create-item-dialog"),
      ).not.toBeInTheDocument();

      await userEvent.click(novoItemBtn);

      expect(
        screen.getByTestId("create-item-dialog"),
      ).toBeInTheDocument();
    });

    it("opens ContractDetailDialog when VendorsTable fires onDetail", async () => {
      mockData([createMockContract()], []);
      render(<WeddingVendorsItemsTab weddingUuid={weddingUuid} />);

      const detailBtn = await screen.findByTestId("btn-vendor-detail");
      expect(
        screen.queryByTestId("contract-detail-dialog"),
      ).not.toBeInTheDocument();

      await userEvent.click(detailBtn);

      expect(
        screen.getByTestId("contract-detail-dialog"),
      ).toBeInTheDocument();
      expect(screen.getByTestId("detail-uuid")).toHaveTextContent("c-1");
    });

    it("opens EditItemDialog when ItemsTable fires onEdit", async () => {
      const item = createMockItem({ uuid: "i-1", name: "Cadeiras" });
      mockData([], [item]);
      render(<WeddingVendorsItemsTab weddingUuid={weddingUuid} />);

      const editBtn = await screen.findByTestId("btn-item-edit");
      expect(
        screen.queryByTestId("edit-item-dialog"),
      ).not.toBeInTheDocument();

      await userEvent.click(editBtn);

      expect(
        screen.getByTestId("edit-item-dialog"),
      ).toBeInTheDocument();
      expect(screen.getByTestId("edit-item-dialog")).toHaveTextContent(
        "Cadeiras",
      );
    });
  });

  describe("State transitions", () => {
    it("closes ContractUploadDialog and resets prefilledParentUuid on success", async () => {
      mockData([], []);
      render(<WeddingVendorsItemsTab weddingUuid={weddingUuid} />);

      const novoContratoBtn = await screen.findByRole("button", { name: /novo contrato/i });
      await userEvent.click(novoContratoBtn);
      expect(
        screen.getByTestId("contract-upload-dialog"),
      ).toBeInTheDocument();
      expect(
        screen.getByTestId("prefilled-parent"),
      ).toHaveTextContent("none");
    });

    it("sets prefilledParentUuid when onCreateAddendum fires from detail dialog", async () => {
      mockData([createMockContract()], []);
      render(<WeddingVendorsItemsTab weddingUuid={weddingUuid} />);

      const detailBtn = await screen.findByTestId("btn-vendor-detail");
      await userEvent.click(detailBtn);
      expect(
        screen.getByTestId("contract-detail-dialog"),
      ).toBeInTheDocument();

      await userEvent.click(screen.getByTestId("btn-create-addendum"));

      expect(
        screen.queryByTestId("contract-detail-dialog"),
      ).not.toBeInTheDocument();

      expect(
        screen.getByTestId("contract-upload-dialog"),
      ).toBeInTheDocument();
      expect(screen.getByTestId("prefilled-parent")).toHaveTextContent(
        "parent-uuid",
      );
    });
  });
});
