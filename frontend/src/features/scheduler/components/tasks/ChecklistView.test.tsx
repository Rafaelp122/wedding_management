import { describe, expect, it, vi } from "vitest";
vi.unmock("@/features/scheduler/components/tasks/ChecklistView");
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { WeddingChecklistTab } from "@/features/scheduler/components/tasks/ChecklistView";

describe("WeddingChecklistTab", () => {
  it("shows loading skeleton initially", () => {
    render(<WeddingChecklistTab weddingUuid="w-1" />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders operational checklist card, title and Novo Item button after loading", async () => {
    render(<WeddingChecklistTab weddingUuid="w-1" />);

    await waitFor(() => {
      expect(
        screen.getByText(/checklist operacional/i),
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /novo item/i }),
      ).toBeInTheDocument();
    });
  });

  it("opens CreateTaskDialog when Novo Item button is clicked", async () => {
    const user = userEvent.setup();
    render(<WeddingChecklistTab weddingUuid="w-1" />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /novo item/i }),
      ).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: /novo item/i }));

    await waitFor(() => {
      expect(screen.getByText("Novo Item de Checklist")).toBeInTheDocument();
      expect(screen.getByLabelText("Título")).toBeInTheDocument();
    });
  });
});

