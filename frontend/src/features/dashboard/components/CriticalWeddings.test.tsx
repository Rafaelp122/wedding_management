import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { CriticalWeddings } from "@/features/dashboard/components/CriticalWeddings";
import { createMockCriticalWedding } from "@/test-data";

describe("CriticalWeddings", () => {
  it("renders nothing when list is empty", () => {
    render(<CriticalWeddings weddings={[]} />);
    expect(
      screen.queryByText(/Casamentos que Precisam de Atenção/),
    ).not.toBeInTheDocument();
  });

  it("renders wedding names", () => {
    render(
      <CriticalWeddings
        weddings={[createMockCriticalWedding()]}
      />,
    );

    expect(
      screen.getByText(/Casamentos que Precisam de Atenção/),
    ).toBeInTheDocument();
    expect(screen.getByText(/João & Maria/)).toBeInTheDocument();
  });

  it("shows days badge", () => {
    render(
      <CriticalWeddings
        weddings={[createMockCriticalWedding({ days_until: 15 })]}
      />,
    );

    expect(screen.getByText("15d")).toBeInTheDocument();
  });

  it("shows destructive badge for <= 30 days", () => {
    render(
      <CriticalWeddings
        weddings={[createMockCriticalWedding({ days_until: 20 })]}
      />,
    );

    const badge = screen.getByText("20d");
    expect(badge.className).toContain("destructive");
  });

  it("shows reason line when overdue tasks exist", () => {
    render(
      <CriticalWeddings
        weddings={[
          createMockCriticalWedding({
            overdue_tasks: 2,
            overdue_installments: 1,
          }),
        ]}
      />,
    );

    expect(
      screen.getByText(/2 tarefas atrasadas • 1 parcela vencida/),
    ).toBeInTheDocument();
  });

  it("shows incomplete task count", () => {
    render(
      <CriticalWeddings
        weddings={[
          createMockCriticalWedding({
            incomplete_tasks: 3,
          }),
        ]}
      />,
    );

    expect(screen.getByText(/3 pendentes/)).toBeInTheDocument();
  });

  it("renders detail link for each wedding", () => {
    render(
      <CriticalWeddings
        weddings={[createMockCriticalWedding({ uuid: "cw-1" })]}
      />,
    );

    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/weddings/cw-1");
  });
});
