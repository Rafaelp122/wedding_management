import { describe, expect, it } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { UpcomingAppointments } from "@/features/dashboard/components/UpcomingAppointments";

describe("UpcomingAppointments", () => {
  it("shows header with period buttons", async () => {
    render(<UpcomingAppointments />);

    await waitFor(() => {
      expect(
        screen.getByText("Próximos Compromissos"),
      ).toBeInTheDocument();
    });

    expect(screen.getByText("7d")).toBeInTheDocument();
    expect(screen.getByText("14d")).toBeInTheDocument();
    expect(screen.getByText("30d")).toBeInTheDocument();
  });

  it("has a link to scheduler page", () => {
    render(<UpcomingAppointments />);

    const link = screen.getByRole("link", { name: /ver agenda completa/i });
    expect(link).toHaveAttribute("href", "/scheduler");
  });

  it("allows changing period", async () => {
    render(<UpcomingAppointments />);

    const user = userEvent.setup();
    await user.click(screen.getByText("30d"));

    expect(
      screen.queryByText(/nenhum compromisso nos próximos 30 dias/i),
    ).toBeDefined();
  });
});
