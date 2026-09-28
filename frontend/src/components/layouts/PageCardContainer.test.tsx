import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PageCardContainer } from "./PageCardContainer";

describe("PageCardContainer", () => {
  it("renders children inside standardized card container", () => {
    render(
      <PageCardContainer data-testid="card-container">
        <table>
          <tbody>
            <tr>
              <td>Linha</td>
            </tr>
          </tbody>
        </table>
      </PageCardContainer>,
    );

    const container = screen.getByTestId("card-container");
    expect(container).toBeInTheDocument();
    expect(container).toHaveClass(
      "bg-card",
      "rounded-xl",
      "border",
      "border-border",
      "shadow-soft",
      "overflow-hidden",
    );
    expect(screen.getByText("Linha")).toBeInTheDocument();
  });
});
