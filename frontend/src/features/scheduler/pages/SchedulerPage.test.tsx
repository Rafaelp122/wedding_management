import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import SchedulerPage from "@/features/scheduler/pages/SchedulerPage";

describe("SchedulerPage", () => {
  it("shows loading state initially", () => {
    render(<SchedulerPage />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders header after loading", async () => {
    render(<SchedulerPage />);

    await waitFor(() => {
      expect(screen.getByText("Scheduler")).toBeInTheDocument();
    });
  });

  it("shows new event button after loading", async () => {
    render(<SchedulerPage />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /novo evento/i }),
      ).toBeInTheDocument();
    });
  });

  it("shows pagination in table view after loading", async () => {
    render(<SchedulerPage />);

    await waitFor(() => {
      const prevButton = screen.getByRole("button", { name: "Anterior" });
      const nextButton = screen.getByRole("button", { name: "Próximo" });
      expect(prevButton).toBeInTheDocument();
      expect(nextButton).toBeInTheDocument();
    });
  });
});
