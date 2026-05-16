import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import NotFoundPage from "@/components/not-found";

describe("NotFoundPage", () => {
  it("renders not found message", () => {
    render(<NotFoundPage />);

    expect(
      screen.getByText("Página não encontrada"),
    ).toBeInTheDocument();
  });

  it("has a link to go to home", () => {
    render(<NotFoundPage />);

    const homeLink = screen.getByRole("link", { name: /ir para o início/i });
    expect(homeLink).toBeInTheDocument();
    expect(homeLink).toHaveAttribute("href", "/");
  });

  it("has a link to go to dashboard", () => {
    render(<NotFoundPage />);

    const dashboardLink = screen.getByRole("link", {
      name: /ir para o painel/i,
    });
    expect(dashboardLink).toBeInTheDocument();
    expect(dashboardLink).toHaveAttribute("href", "/dashboard");
  });
});
