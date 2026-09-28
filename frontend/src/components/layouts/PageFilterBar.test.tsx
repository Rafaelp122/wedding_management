import { render, screen, fireEvent } from "@/test-utils";
import { describe, it, expect, vi } from "vitest";
import { PageFilterBar } from "./PageFilterBar";

describe("PageFilterBar", () => {
  it("renders search input and calls onSearchChange when typed", () => {
    const handleSearchChange = vi.fn();
    render(
      <PageFilterBar
        search="termo"
        onSearchChange={handleSearchChange}
        searchPlaceholder="Buscar por nome..."
      />,
    );

    const input = screen.getByPlaceholderText("Buscar por nome...");
    expect(input).toBeInTheDocument();
    expect(input).toHaveValue("termo");
    expect(input).toHaveAttribute("aria-label", "Buscar por nome...");

    fireEvent.change(input, { target: { value: "novo termo" } });
    expect(handleSearchChange).toHaveBeenCalledWith("novo termo");
  });

  it("renders search input with default placeholder and handles undefined search value", () => {
    const handleSearchChange = vi.fn();
    render(<PageFilterBar onSearchChange={handleSearchChange} />);

    const input = screen.getByPlaceholderText("Buscar...");
    expect(input).toBeInTheDocument();
    expect(input).toHaveValue("");
    expect(input).toHaveAttribute("aria-label", "Buscar...");
  });

  it("does not render search input when onSearchChange is not provided", () => {
    render(<PageFilterBar search="termo" />);

    expect(screen.queryByPlaceholderText("Buscar...")).not.toBeInTheDocument();
  });

  it("renders children filter slots when provided", () => {
    render(
      <PageFilterBar>
        <select data-testid="status-select">
          <option value="all">Todos</option>
        </select>
      </PageFilterBar>,
    );

    expect(screen.getByTestId("status-select")).toBeInTheDocument();
  });
});
