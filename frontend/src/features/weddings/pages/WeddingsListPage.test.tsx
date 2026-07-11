import { describe, expect, it } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import WeddingsListPage from "@/features/weddings/pages/WeddingsListPage";

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
        screen.queryByRole("table") || screen.queryByText(/Nenhum casamento/i)
      ).not.toBeNull();
    });

    const user = userEvent.setup();
    const createBtn = screen.getByRole("button", { name: /novo casamento/i });
    await user.click(createBtn);

    // Deve abrir o formulário
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Novo Casamento" })).toBeInTheDocument();
    });
  });

  it("allows searching weddings by text", async () => {
    render(<WeddingsListPage />);

    await waitFor(() => {
      expect(
        screen.queryByRole("table") || screen.queryByText(/Nenhum casamento/i)
      ).not.toBeNull();
    });

    const searchInput = screen.getByPlaceholderText(/buscar por noivos ou local/i);
    const user = userEvent.setup();
    await user.type(searchInput, "Casal Teste");

    expect(searchInput).toHaveValue("Casal Teste");
  });
});
