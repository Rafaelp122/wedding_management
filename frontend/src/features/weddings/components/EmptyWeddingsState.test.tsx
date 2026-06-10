import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { EmptyWeddingsState } from "@/features/weddings/components/EmptyWeddingsState";

describe("EmptyWeddingsState", () => {
  it("renders headline and description", () => {
    render(<EmptyWeddingsState onCreateClick={vi.fn()} />);

    expect(
      screen.getByText("Sua tela em branco para criar memórias."),
    ).toBeInTheDocument();
  });

  it("renders both CTA buttons", () => {
    render(<EmptyWeddingsState onCreateClick={vi.fn()} />);

    expect(
      screen.getByRole("button", { name: /cadastrar primeiro casamento/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /carregar exemplo prático/i }),
    ).toBeInTheDocument();
  });

  it("calls onCreateClick when primary button clicked", async () => {
    const onCreateClick = vi.fn();
    render(<EmptyWeddingsState onCreateClick={onCreateClick} />);

    const user = userEvent.setup();
    await user.click(
      screen.getByRole("button", { name: /cadastrar primeiro casamento/i }),
    );

    expect(onCreateClick).toHaveBeenCalledOnce();
  });
});
