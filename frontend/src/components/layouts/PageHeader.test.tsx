import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PageHeader } from "./PageHeader";

describe("PageHeader", () => {
  it("renders title correctly", () => {
    render(<PageHeader title="Minha Página" />);

    const titleElement = screen.getByRole("heading", { level: 1 });
    expect(titleElement).toHaveTextContent("Minha Página");
    expect(titleElement).toHaveClass("font-display", "font-bold");
  });

  it("renders description when provided", () => {
    render(
      <PageHeader
        title="Minha Página"
        description="Descrição detalhada da página"
      />,
    );

    expect(
      screen.getByText("Descrição detalhada da página"),
    ).toBeInTheDocument();
  });

  it("renders actions slot when provided", () => {
    render(
      <PageHeader
        title="Minha Página"
        actions={<button>Ação</button>}
      />,
    );

    expect(screen.getByRole("button", { name: "Ação" })).toBeInTheDocument();
  });
});
