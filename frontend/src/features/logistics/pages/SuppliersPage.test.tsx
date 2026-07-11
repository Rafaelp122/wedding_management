import { describe, expect, it } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import SuppliersPage from "@/features/logistics/pages/SuppliersPage";

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
  });
});
