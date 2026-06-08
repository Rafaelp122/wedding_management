import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { Logo } from "@/components/logo";

describe("Logo", () => {
  it("renders the logo icon and text", () => {
    render(<Logo />);

    expect(screen.getByText("Sim, Aceito!")).toBeInTheDocument();
  });

  it("renders as a plain div when href is not provided", () => {
    const { container } = render(<Logo />);

    const link = container.querySelector("a");
    expect(link).toBeNull();
  });

  it("renders as an anchor when href is provided", () => {
    render(<Logo href="https://example.com" />);

    const link = screen.getByRole("link");
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "https://example.com");
  });

  it("accepts custom classNames", () => {
    render(
      <Logo
        className="custom-gap"
        iconClassName="custom-icon"
        textClassName="custom-text"
      />,
    );

    expect(screen.getByText("Sim, Aceito!")).toHaveClass("custom-text");
  });
});
