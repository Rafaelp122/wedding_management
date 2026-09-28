import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PageContainer } from "./PageContainer";

describe("PageContainer", () => {
  it("renders children with standard container classes", () => {
    render(
      <PageContainer data-testid="container">
        <div>Conteúdo da página</div>
      </PageContainer>,
    );

    const container = screen.getByTestId("container");
    expect(container).toBeInTheDocument();
    expect(container).toHaveClass("max-w-7xl", "mx-auto", "space-y-6");
    expect(screen.getByText("Conteúdo da página")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(
      <PageContainer data-testid="container" className="custom-class">
        <div>Conteúdo</div>
      </PageContainer>,
    );

    const container = screen.getByTestId("container");
    expect(container).toHaveClass("custom-class");
  });
});
