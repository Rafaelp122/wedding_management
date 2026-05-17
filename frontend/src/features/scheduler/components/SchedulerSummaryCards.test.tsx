import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { SchedulerSummaryCards } from "@/features/scheduler/components/SchedulerSummaryCards";

describe("SchedulerSummaryCards", () => {
  it("renders all 3 summary cards with correct data from props", () => {
    const summary = { total: 42, upcoming: 7, withReminder: 15 };
    render(<SchedulerSummaryCards summary={summary} />);

    expect(screen.getByText("Eventos")).toBeInTheDocument();
    expect(screen.getByText("Próximos 7 dias")).toBeInTheDocument();
    expect(screen.getByText("Com lembrete")).toBeInTheDocument();

    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.getByText("15")).toBeInTheDocument();
  });

  it("renders zero values correctly", () => {
    const summary = { total: 0, upcoming: 0, withReminder: 0 };
    render(<SchedulerSummaryCards summary={summary} />);

    const zeros = screen.getAllByText("0");
    expect(zeros).toHaveLength(3);
  });

  it("renders large numbers without formatting issues", () => {
    const summary = { total: 999999, upcoming: 12345, withReminder: 98765 };
    render(<SchedulerSummaryCards summary={summary} />);

    expect(screen.getByText("999999")).toBeInTheDocument();
    expect(screen.getByText("12345")).toBeInTheDocument();
    expect(screen.getByText("98765")).toBeInTheDocument();
  });
});
