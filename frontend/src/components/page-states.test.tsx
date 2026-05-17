import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import {
  ListPageLoadingState,
  ListPageErrorState,
} from "@/components/page-states";

describe("ListPageLoadingState", () => {
  it("renders skeleton placeholders", () => {
    render(<ListPageLoadingState />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThanOrEqual(2);
  });
});

describe("ListPageErrorState", () => {
  it("renders error message", () => {
    render(<ListPageErrorState message="Falha ao carregar." />);

    expect(screen.getByText("Erro ao carregar dados")).toBeInTheDocument();
    expect(screen.getByText("Falha ao carregar.")).toBeInTheDocument();
  });

  it("renders retry button when onRetry is provided", () => {
    const onRetry = vi.fn();
    render(
      <ListPageErrorState message="Erro" onRetry={onRetry} />,
    );

    const btn = screen.getByRole("button", { name: /tentar novamente/i });
    expect(btn).toBeInTheDocument();
  });

  it("does not render retry button when onRetry is not provided", () => {
    render(<ListPageErrorState message="Erro" />);

    expect(
      screen.queryByRole("button", { name: /tentar novamente/i }),
    ).not.toBeInTheDocument();
  });

  it("calls onRetry when retry button is clicked", async () => {
    const onRetry = vi.fn();
    render(
      <ListPageErrorState message="Erro" onRetry={onRetry} />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /tentar novamente/i }));

    expect(onRetry).toHaveBeenCalledOnce();
  });
});
