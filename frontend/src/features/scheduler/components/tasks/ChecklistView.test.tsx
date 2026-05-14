import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import { WeddingChecklistTab } from "@/features/scheduler/components/tasks/ChecklistView";

describe("WeddingChecklistTab", () => {
  it("shows loading skeleton initially", () => {
    render(<WeddingChecklistTab weddingUuid="w-1" />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders checklist card after loading", async () => {
    render(<WeddingChecklistTab weddingUuid="w-1" />);

    await waitFor(() => {
      expect(
        screen.getByText(/checklist do planejamento/i),
      ).toBeInTheDocument();
    });
  });
});
