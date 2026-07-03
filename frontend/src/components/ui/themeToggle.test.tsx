import { describe, expect, it } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { ThemeToggle } from "./themeToggle";

describe("ThemeToggle", () => {
  it("renders with correct aria-label", () => {
    render(<ThemeToggle />);
    expect(screen.getByLabelText("Alternar tema")).toBeInTheDocument();
  });

  it("shows tooltip on hover", async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = screen.getByLabelText("Alternar tema");
    await user.hover(button);

    // Check for the tooltip content in the body using role="tooltip" or by text
    // We use waitFor to handle potential delays
    await waitFor(() => {
      expect(screen.getByRole("tooltip", { name: "Alternar tema" })).toBeInTheDocument();
    });
  });
});
