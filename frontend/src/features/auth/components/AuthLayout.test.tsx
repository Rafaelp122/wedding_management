import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { AuthLayout } from "@/features/auth/components/AuthLayout";

const defaultProps = {
  heroQuote: "A great quote.",
  heroBadgeLabel: "// Label",
  heroBoxTitle: "Box Title",
  heroBoxSubtitle: "Box Subtitle",
  heroBoxBadge: "100%",
  heroBoxLeftLabel: "Left",
  heroBoxLeftValue: "$100",
  heroBoxRightLabel: "Right",
  heroBoxRightValue: "$200",
};

describe("AuthLayout", () => {
  it("renders children content", () => {
    render(
      <AuthLayout {...defaultProps}>
        <p>Form content here</p>
      </AuthLayout>,
    );

    expect(screen.getByText("Form content here")).toBeInTheDocument();
  });

  it("renders the logo linking to the landing page", () => {
    render(
      <AuthLayout {...defaultProps}>
        <p>Child</p>
      </AuthLayout>,
    );

    const logoLink = screen.getByRole("link");
    expect(logoLink).toBeInTheDocument();
    expect(logoLink).toHaveAttribute("href", "https://simaceito.site/");
  });

  it("renders hero quote and badge", () => {
    render(
      <AuthLayout {...defaultProps}>
        <p>Child</p>
      </AuthLayout>,
    );

    expect(screen.getByText("A great quote.")).toBeInTheDocument();
    expect(screen.getByText("// Label")).toBeInTheDocument();
  });

  it("renders hero box content", () => {
    render(
      <AuthLayout {...defaultProps}>
        <p>Child</p>
      </AuthLayout>,
    );

    expect(screen.getByText("Box Title")).toBeInTheDocument();
    expect(screen.getByText("100%")).toBeInTheDocument();
    expect(screen.getByText("$100")).toBeInTheDocument();
    expect(screen.getByText("$200")).toBeInTheDocument();
  });

  it("renders theme toggle button", () => {
    render(
      <AuthLayout {...defaultProps}>
        <p>Child</p>
      </AuthLayout>,
    );

    const toggle = screen.getByRole("switch");
    expect(toggle).toBeInTheDocument();
  });
});
