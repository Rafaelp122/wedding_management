import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import WeddingsListPage from "@/features/weddings/pages/WeddingsListPage";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";
import { createMockWedding } from "@/test-data";

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockWedding = createMockWedding({
  uuid: "wedding-123",
  groom_name: "João",
  bride_name: "Maria",
  location: "Buffet Castelo",
  date: "2026-10-15",
  status: "IN_PROGRESS",
  total_budget: 50000,
});

describe("WeddingsListPage", () => {
  it("shows loading state initially", () => {
    render(<WeddingsListPage />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders header after loading", async () => {
    render(<WeddingsListPage />);

    await waitFor(() => {
      expect(screen.getByText("Casamentos")).toBeInTheDocument();
    });
  });

  it("shows create button after loading", async () => {
    render(<WeddingsListPage />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /novo casamento/i }),
      ).toBeInTheDocument();
    });
  });

  it("shows filter search field after loading", async () => {
    render(<WeddingsListPage />);

    await waitFor(() => {
      expect(
        screen.getByPlaceholderText(/buscar por noivos ou local/i),
      ).toBeInTheDocument();
    });
  });

  it("renders weddings list and allows opening the create dialog", async () => {
    render(<WeddingsListPage />);

    // Espera o carregamento sumir
    await waitFor(() => {
      expect(
        screen.queryByRole("table") || screen.queryByText(/Nenhum casamento/i),
      ).not.toBeNull();
    });

    const user = userEvent.setup();
    const createBtn = screen.getByRole("button", { name: /novo casamento/i });
    await user.click(createBtn);

    // Deve abrir o formulário
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "Novo Casamento" }),
      ).toBeInTheDocument();
    });
  });

  it("allows searching weddings by text", async () => {
    render(<WeddingsListPage />);

    await waitFor(() => {
      expect(
        screen.queryByRole("table") || screen.queryByText(/Nenhum casamento/i),
      ).not.toBeNull();
    });

    const searchInput = screen.getByPlaceholderText(
      /buscar por noivos ou local/i,
    );
    const user = userEvent.setup();
    await user.type(searchInput, "Casal Teste");

    expect(searchInput).toHaveValue("Casal Teste");
  });

  it("shows error state when query fails and recovers on retry", async () => {
    let shouldFail = true;

    server.use(
      http.get("*/api/v1/weddings/", () => {
        if (shouldFail) {
          return HttpResponse.json({ detail: "Erro interno" }, { status: 500 });
        }
        return HttpResponse.json(
          { items: [mockWedding], count: 1 },
          { status: 200 },
        );
      }),
    );

    render(<WeddingsListPage />);

    // Assert error state is displayed
    expect(await screen.findByText("Erro interno")).toBeInTheDocument();

    // Now set API to succeed, and click retry
    shouldFail = false;
    const user = userEvent.setup();
    const retryBtn = screen.getByRole("button", { name: /tentar novamente/i });
    await user.click(retryBtn);

    // Verify it recovers and shows the list
    expect(await screen.findByText("João & Maria")).toBeInTheDocument();
  });

  it("shows empty weddings state when count is 0 and items is empty", async () => {
    server.use(
      http.get("*/api/v1/weddings/", () => {
        return HttpResponse.json({ items: [], count: 0 }, { status: 200 });
      }),
    );

    render(<WeddingsListPage />);

    expect(
      await screen.findByText(/Cada grande assessoria de casamentos/i),
    ).toBeInTheDocument();
  });

  it("opens the create dialog from the empty state", async () => {
    server.use(
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
    );
    render(<WeddingsListPage />);

    await userEvent.click(
      await screen.findByRole("button", {
        name: /cadastrar primeiro casamento/i,
      }),
    );

    expect(
      screen.getByRole("heading", { name: "Novo Casamento" }),
    ).toBeInTheDocument();
  });

  it("creates a wedding and closes the dialog", async () => {
    server.use(
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
      http.post("*/api/v1/weddings/", () => HttpResponse.json(mockWedding)),
    );
    render(<WeddingsListPage />);

    const user = userEvent.setup();
    await user.click(
      await screen.findByRole("button", { name: /novo casamento/i }),
    );
    await user.type(screen.getByLabelText("Nome do Noivo"), "João");
    await user.type(screen.getByLabelText("Nome da Noiva"), "Maria");
    await user.type(screen.getByLabelText("Local"), "Buffet Castelo");
    await user.type(screen.getByLabelText("Data do Casamento"), "2027-10-15");
    await user.click(screen.getByRole("button", { name: /criar casamento/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Casamento criado com sucesso!",
      );
      expect(
        screen.queryByRole("heading", { name: "Novo Casamento" }),
      ).not.toBeInTheDocument();
    });
  });

  it("shows no weddings found warning when search result is empty but totalCount > 0", async () => {
    server.use(
      http.get("*/api/v1/weddings/", () => {
        return HttpResponse.json({ items: [], count: 3 }, { status: 200 });
      }),
    );

    render(<WeddingsListPage />);

    expect(
      await screen.findByText("Nenhum casamento encontrado"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Tente ajustar os filtros de busca"),
    ).toBeInTheDocument();
  });

  it("allows navigating to wedding details page on row click", async () => {
    server.use(
      http.get("*/api/v1/weddings/", () => {
        return HttpResponse.json(
          { items: [mockWedding], count: 1 },
          { status: 200 },
        );
      }),
    );

    render(<WeddingsListPage />);

    // Click row using text
    const cell = await screen.findByText("João & Maria");
    const user = userEvent.setup();
    await user.click(cell);

    expect(mockNavigate).toHaveBeenCalledWith(`/weddings/${mockWedding.uuid}`);
  });

  it("loads the next page", async () => {
    const secondPageWedding = createMockWedding({
      uuid: "wedding-page-2",
      groom_name: "Carlos",
      bride_name: "Ana",
    });
    server.use(
      http.get("*/api/v1/weddings/", ({ request }) => {
        const offset = new URL(request.url).searchParams.get("offset");
        return HttpResponse.json({
          items: offset === "5" ? [secondPageWedding] : [mockWedding],
          count: 11,
        });
      }),
    );
    render(<WeddingsListPage />);

    await screen.findByText("João & Maria");
    await userEvent.click(screen.getByRole("button", { name: "Próximo" }));

    expect(await screen.findByText("Carlos & Ana")).toBeInTheDocument();
  });

  it("allows editing a wedding in EditWeddingDialog", async () => {
    server.use(
      http.get("*/api/v1/weddings/", () => {
        return HttpResponse.json(
          { items: [mockWedding], count: 1 },
          { status: 200 },
        );
      }),
      http.put("*/api/v1/weddings/:uuid/", () => {
        return HttpResponse.json(mockWedding, { status: 200 });
      }),
    );

    render(<WeddingsListPage />);
    const user = userEvent.setup();

    // Click "Editar" button inside action menu
    const editBtn = await screen.findByRole("button", { name: "Editar" });
    await user.click(editBtn);

    // Verify dialog is open
    expect(
      await screen.findByRole("heading", { name: "Editar Casamento" }),
    ).toBeInTheDocument();

    // Click save button
    const saveBtn = screen.getByRole("button", { name: "Salvar Alterações" });
    await user.click(saveBtn);

    // Verify success toast
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Casamento atualizado com sucesso!",
      );
    });
  });

  it("closes the edit dialog on cancel", async () => {
    server.use(
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({ items: [mockWedding], count: 1 }),
      ),
    );
    render(<WeddingsListPage />);

    await userEvent.click(
      await screen.findByRole("button", { name: "Editar" }),
    );
    await userEvent.click(screen.getByRole("button", { name: /cancelar/i }));

    expect(
      screen.queryByRole("heading", { name: "Editar Casamento" }),
    ).not.toBeInTheDocument();
  });

  it("allows deleting a wedding in DeleteWeddingDialog", async () => {
    server.use(
      http.get("*/api/v1/weddings/", () => {
        return HttpResponse.json(
          { items: [mockWedding], count: 1 },
          { status: 200 },
        );
      }),
      http.delete("*/api/v1/weddings/:uuid/", () => {
        return new HttpResponse(null, { status: 204 });
      }),
    );

    render(<WeddingsListPage />);
    const user = userEvent.setup();

    // Click "Excluir" button inside action menu
    const deleteBtn = await screen.findByRole("button", { name: "Excluir" });
    await user.click(deleteBtn);

    // Verify dialog is open
    expect(
      await screen.findByRole("heading", { name: "Deletar Casamento" }),
    ).toBeInTheDocument();

    // Type name to confirm
    const confirmInput = screen.getByPlaceholderText("Digite o nome aqui...");
    await user.type(confirmInput, "João & Maria");

    // Click delete button
    const confirmBtn = screen.getByRole("button", {
      name: "Deletar Permanentemente",
    });
    await user.click(confirmBtn);

    // Verify success toast
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Casamento deletado com sucesso!",
      );
    });
  });

  it("closes the delete dialog on cancel", async () => {
    server.use(
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({ items: [mockWedding], count: 1 }),
      ),
    );
    render(<WeddingsListPage />);

    await userEvent.click(
      await screen.findByRole("button", { name: "Excluir" }),
    );
    await userEvent.click(screen.getByRole("button", { name: /cancelar/i }));

    expect(
      screen.queryByRole("heading", { name: "Deletar Casamento" }),
    ).not.toBeInTheDocument();
  });
});
