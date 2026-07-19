import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { UrgentTasksList } from "./UrgentTasksList";

describe("UrgentTasksList", () => {
  it("renders empty state when no tasks are provided", () => {
    render(<UrgentTasksList tasks={[]} />);
    expect(screen.getByText("Tudo em dia por aqui!")).toBeInTheDocument();
  });

  it("renders list of urgent tasks", () => {
    const mockTasks = [
      { uuid: "t-1", title: "Task 1", due_date: "2026-08-01" },
      { uuid: "t-2", title: "Task 2", due_date: "2026-08-15" },
    ];

    render(<UrgentTasksList tasks={mockTasks} />);

    expect(screen.getByText("Task 1")).toBeInTheDocument();
    expect(screen.getByText("Task 2")).toBeInTheDocument();
    expect(screen.getAllByText("Prioridade: Alta")).toHaveLength(2);
  });
});
