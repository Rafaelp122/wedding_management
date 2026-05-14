import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
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

  it("shows filter fields after loading", async () => {
    render(<WeddingsListPage />);

    await waitFor(() => {
      expect(
        screen.getByPlaceholderText(/buscar por nome dos noivos/i),
      ).toBeInTheDocument();
    });
  });
});
