import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingChecklistTable } from "@/features/scheduler/components/tasks/ChecklistTable";
import { createMockTask } from "@/test-data";

const mockTasks = [
  createMockTask({ uuid: "t-1", title: "Contratar buffet", description: "Pesquisar e fechar contrato", due_date: "2025-03-15", is_completed: false }),
  createMockTask({ uuid: "t-2", title: "Escolher local", description: null, due_date: null, is_completed: true }),
];

describe("WeddingChecklistTable", () => {
  it("shows empty state when no tasks", () => {
    render(
      <WeddingChecklistTable
        tasks={[]}
        onToggle={vi.fn()}
        isUpdating={false}
      />,
    );

    expect(
      screen.getByText(/nenhuma tarefa registrada/i),
    ).toBeInTheDocument();
  });

  it("renders task titles", () => {
    render(
      <WeddingChecklistTable
        tasks={mockTasks}
        onToggle={vi.fn()}
        isUpdating={false}
      />,
    );

    expect(screen.getByText("Contratar buffet")).toBeInTheDocument();
    expect(screen.getByText("Escolher local")).toBeInTheDocument();
  });

  it("shows completed task with line-through", () => {
    render(
      <WeddingChecklistTable
        tasks={mockTasks}
        onToggle={vi.fn()}
        isUpdating={false}
      />,
    );

    const completedLabel = screen.getByText("Escolher local");
    expect(completedLabel.className).toContain("line-through");
  });

  it("renders due date when present", () => {
    render(
      <WeddingChecklistTable
        tasks={mockTasks}
        onToggle={vi.fn()}
        isUpdating={false}
      />,
    );

    expect(screen.getByText(/prazo/i)).toBeInTheDocument();
  });

  it("calls onToggle when checkbox is clicked", async () => {
    const onToggle = vi.fn();
    render(
      <WeddingChecklistTable
        tasks={mockTasks}
        onToggle={onToggle}
        isUpdating={false}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByLabelText("Contratar buffet"));

    expect(onToggle).toHaveBeenCalledWith("t-1", false);
  });

  it("disables checkboxes when isUpdating", () => {
    render(
      <WeddingChecklistTable
        tasks={mockTasks}
        onToggle={vi.fn()}
        isUpdating={true}
      />,
    );

    const checkbox = screen.getByLabelText("Contratar buffet");
    expect(checkbox).toBeDisabled();
  });
});
