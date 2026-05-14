import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import { WeddingTimelineTab } from "@/features/scheduler/components/events/TimelineView";

describe("WeddingTimelineTab", () => {
  it("shows loading skeleton initially", () => {
    render(<WeddingTimelineTab weddingUuid="w-1" />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders timeline card after loading", async () => {
    render(<WeddingTimelineTab weddingUuid="w-1" />);

    await waitFor(() => {
      expect(
        screen.getByText(/cronograma de eventos/i),
      ).toBeInTheDocument();
    });
  });
});
