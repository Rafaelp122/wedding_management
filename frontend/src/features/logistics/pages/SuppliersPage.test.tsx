import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
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
});
