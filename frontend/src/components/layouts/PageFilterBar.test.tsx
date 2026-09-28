import { render, screen, fireEvent } from "@testing-library/react";
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

    fireEvent.change(input, { target: { value: "novo termo" } });
    expect(handleSearchChange).toHaveBeenCalledWith("novo termo");
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
