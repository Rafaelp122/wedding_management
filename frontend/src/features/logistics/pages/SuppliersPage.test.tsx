import { describe, expect, it } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import SuppliersPage from "@/features/logistics/pages/SuppliersPage";
import { createMockSupplier } from "@/test-data";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";

const supplier = createMockSupplier({
  uuid: "supplier-123",
  name: "Buffet Primavera",
});

function mockSuppliers(items = [supplier], count = items.length) {
  server.use(
    http.get("*/api/v1/logistics/suppliers/", () =>
      HttpResponse.json({ items, count }),
    ),
  );
}

describe("SuppliersPage", () => {
  it("shows loading state initially", () => {
    render(<SuppliersPage />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders header after loading", async () => {
    render(<SuppliersPage />);

    await waitFor(() => {
      expect(screen.getByText("Fornecedores")).toBeInTheDocument();
    });
  });

  it("shows create button after loading", async () => {
    render(<SuppliersPage />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /novo fornecedor/i }),
      ).toBeInTheDocument();
    });
  });

  it("shows search input after loading", async () => {
    render(<SuppliersPage />);

    await waitFor(() => {
      expect(
        screen.getByPlaceholderText(/buscar por nome/i),
      ).toBeInTheDocument();
    });
  });

  it("renders suppliers list and allows opening the create form", async () => {
    render(<SuppliersPage />);

    // Espera o carregamento sumir
    await waitFor(() => {
      expect(screen.queryByText("Carregando...")).not.toBeInTheDocument();
    });

    const user = userEvent.setup();
    const createBtn = screen.getByRole("button", { name: /novo fornecedor/i });
    await user.click(createBtn);

    // Deve abrir o formulário
    await waitFor(() => {
      expect(screen.getByText("Novo fornecedor")).toBeInTheDocument();
    });
  });

  it("allows searching suppliers by text", async () => {
    render(<SuppliersPage />);

    await waitFor(() => {
      expect(screen.queryByText("Carregando...")).not.toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/buscar por nome/i);
    const user = userEvent.setup();
    await user.type(searchInput, "Fornecedor Teste");

    expect(searchInput).toHaveValue("Fornecedor Teste");
  }, 15000);

  it("shows the API error and retries the request", async () => {
    let shouldFail = true;
    server.use(
      http.get("*/api/v1/logistics/suppliers/", () =>
        shouldFail
          ? HttpResponse.json({ detail: "Falha ao listar" }, { status: 500 })
          : HttpResponse.json({ items: [supplier], count: 1 }),
      ),
    );

    render(<SuppliersPage />);

    expect(await screen.findByText("Falha ao listar")).toBeInTheDocument();
    shouldFail = false;
    await userEvent.click(
      screen.getByRole("button", { name: /tentar novamente/i }),
    );

    expect(await screen.findByText("Buffet Primavera")).toBeInTheDocument();
  });

  it("renders the unfiltered empty state", async () => {
    mockSuppliers([]);

    render(<SuppliersPage />);

    expect(
      await screen.findByRole("heading", {
        name: "Nenhum fornecedor encontrado",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Clique em 'Novo Fornecedor' para começar"),
    ).toBeInTheDocument();
  });

  it("renders the filtered empty state after searching", async () => {
    mockSuppliers([]);
    render(<SuppliersPage />);

    const search = await screen.findByPlaceholderText(/buscar por nome/i);
    await userEvent.type(search, "inexistente");

    expect(
      await screen.findByText("Tente ajustar os filtros de busca"),
    ).toBeInTheDocument();
  });

  it("filters active suppliers", async () => {
    let activeFilter: string | null = null;
    server.use(
      http.get("*/api/v1/logistics/suppliers/", ({ request }) => {
        activeFilter = new URL(request.url).searchParams.get("is_active");
        return HttpResponse.json({ items: [supplier], count: 1 });
      }),
    );
    render(<SuppliersPage />);

    await screen.findByText("Buffet Primavera");
    await userEvent.click(screen.getByRole("combobox"));
    await userEvent.click(screen.getByRole("option", { name: "Ativos" }));

    await waitFor(() => expect(activeFilter).toBe("true"));

    await userEvent.click(screen.getByRole("combobox"));
    await userEvent.click(screen.getByRole("option", { name: "Inativos" }));

    await waitFor(() => expect(activeFilter).toBe("false"));
  });

  it("refetches suppliers after creation", async () => {
    let listRequests = 0;
    server.use(
      http.get("*/api/v1/logistics/suppliers/", () => {
        listRequests += 1;
        return HttpResponse.json({ items: [], count: 0 });
      }),
      http.post("*/api/v1/logistics/suppliers/", () =>
        HttpResponse.json(supplier),
      ),
    );
    render(<SuppliersPage />);

    await userEvent.click(
      await screen.findByRole("button", { name: /novo fornecedor/i }),
    );
    await userEvent.type(screen.getByLabelText("Nome"), "Buffet Primavera");
    await userEvent.type(
      screen.getByLabelText("CNPJ"),
      "12.345.678/0001-90",
    );
    await userEvent.click(screen.getByRole("button", { name: "Salvar" }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Fornecedor criado com sucesso!",
      );
      expect(listRequests).toBeGreaterThan(1);
    });
  });

  it("loads the next page", async () => {
    const pageTwoSupplier = createMockSupplier({
      uuid: "supplier-page-2",
      name: "Fotografia Aurora",
    });
    server.use(
      http.get("*/api/v1/logistics/suppliers/", ({ request }) => {
        const offset = new URL(request.url).searchParams.get("offset");
        return HttpResponse.json({
          items: offset === "10" ? [pageTwoSupplier] : [supplier],
          count: 11,
        });
      }),
    );
    render(<SuppliersPage />);

    await screen.findByText("Buffet Primavera");
    await userEvent.click(screen.getByRole("button", { name: "Próximo" }));

    expect(await screen.findByText("Fotografia Aurora")).toBeInTheDocument();
  });

  it("opens supplier details when a row is clicked", async () => {
    mockSuppliers();
    server.use(
      http.get("*/api/v1/logistics/suppliers/:uuid/", () =>
        HttpResponse.json(supplier),
      ),
    );
    render(<SuppliersPage />);

    await userEvent.click(await screen.findByText("Buffet Primavera"));

    expect(
      await screen.findByRole("heading", { name: "Buffet Primavera" }),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(
      screen.queryByRole("heading", { name: "Buffet Primavera" }),
    ).not.toBeInTheDocument();
  });

  it("opens the edit and delete dialogs from the row actions", async () => {
    mockSuppliers();
    render(<SuppliersPage />);

    await screen.findByText("Buffet Primavera");
    const actions = screen.getByRole("button", { name: /ações/i });
    await userEvent.click(actions);
    await userEvent.click(screen.getByText("Editar"));
    expect(
      await screen.findByRole("heading", { name: "Editar fornecedor" }),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /cancelar/i }));
    await userEvent.click(actions);
    await userEvent.click(screen.getByText("Deletar"));
    expect(
      await screen.findByRole("heading", { name: "Excluir fornecedor" }),
    ).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /cancelar/i }));
    expect(
      screen.queryByRole("heading", { name: "Excluir fornecedor" }),
    ).not.toBeInTheDocument();
  });

  it("deletes a supplier from the confirmation dialog", async () => {
    mockSuppliers();
    server.use(
      http.delete("*/api/v1/logistics/suppliers/:uuid/", () =>
        HttpResponse.json(null, { status: 204 }),
      ),
    );
    render(<SuppliersPage />);

    await screen.findByText("Buffet Primavera");
    await userEvent.click(screen.getByRole("button", { name: /ações/i }));
    await userEvent.click(screen.getByText("Deletar"));
    await userEvent.click(
      screen.getByRole("button", { name: "Deletar Permanentemente" }),
    );

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Fornecedor removido com sucesso!",
      );
      expect(
        screen.queryByRole("heading", { name: "Excluir fornecedor" }),
      ).not.toBeInTheDocument();
    });
  });
});
