import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingHeader } from "./WeddingHeader";
import { createMockWedding } from "@/test-data";

const mockWedding = createMockWedding({
  groom_name: "João",
  bride_name: "Maria",
  location: "Fazenda Vila Rica",
  expected_guests: 150,
  total_budget: "75000",
  template: "beach_6m",
  status: "IN_PROGRESS",
});

describe("WeddingHeader", () => {
  it("renders names, template, location and guests info", () => {
    const onEditClick = vi.fn();
    render(
      <WeddingHeader
        wedding={mockWedding}
        displayDate="15 Set 2026"
        checklistPercentage={45}
        onEditClick={onEditClick}
      />
    );

    expect(screen.getByText("João & Maria")).toBeInTheDocument();
    expect(screen.getByText("Campestre")).toBeInTheDocument(); // beach_6m mapping
    expect(screen.getByText("Fazenda Vila Rica")).toBeInTheDocument();
    expect(screen.getByText("150 Convidados")).toBeInTheDocument();
    expect(screen.getByText("15 Set 2026")).toBeInTheDocument();
  });

  it("renders budget and checklist percentage", () => {
    const onEditClick = vi.fn();
    render(
      <WeddingHeader
        wedding={mockWedding}
        displayDate="15 Set 2026"
        checklistPercentage={45}
        onEditClick={onEditClick}
      />
    );

    expect(screen.getByText("R$ 75k")).toBeInTheDocument();
    expect(screen.getByText("45%")).toBeInTheDocument();
  });

  it("calls onEditClick callback when edit button is clicked", async () => {
    const onEditClick = vi.fn();
    render(
      <WeddingHeader
        wedding={mockWedding}
        displayDate="15 Set 2026"
        checklistPercentage={45}
        onEditClick={onEditClick}
      />
    );

    const editBtn = screen.getByTitle("Editar dados do casamento");
    await userEvent.click(editBtn);

    expect(onEditClick).toHaveBeenCalledTimes(1);
  });

  it("calls onCancelClick when cancel button is clicked", async () => {
    const onCancelClick = vi.fn();
    render(
      <WeddingHeader
        wedding={mockWedding}
        displayDate="15 Set 2026"
        checklistPercentage={45}
        onEditClick={vi.fn()}
        onCancelClick={onCancelClick}
      />
    );

    const cancelBtn = screen.getByTitle("Cancelar casamento");
    await userEvent.click(cancelBtn);

    expect(onCancelClick).toHaveBeenCalledTimes(1);
  });

  it("calls onCompleteClick when complete button is clicked and can_complete is true", async () => {
    const onCompleteClick = vi.fn();
    const readyWedding = createMockWedding({
      ...mockWedding,
      can_complete: true,
    });

    render(
      <WeddingHeader
        wedding={readyWedding}
        displayDate="01 Jan 2020"
        checklistPercentage={100}
        onEditClick={vi.fn()}
        onCompleteClick={onCompleteClick}
      />
    );

    const completeBtn = screen.getByTitle("Concluir casamento");
    expect(completeBtn).not.toBeDisabled();
    await userEvent.click(completeBtn);

    expect(onCompleteClick).toHaveBeenCalledTimes(1);
  });

  it("disables complete button when can_complete is false", () => {
    const onCompleteClick = vi.fn();
    const notReadyWedding = createMockWedding({
      ...mockWedding,
      can_complete: false,
    });

    render(
      <WeddingHeader
        wedding={notReadyWedding}
        displayDate="31 Dez 2099"
        checklistPercentage={10}
        onEditClick={vi.fn()}
        onCompleteClick={onCompleteClick}
      />
    );

    const completeBtn = screen.getByTitle(
      "O casamento só pode ser concluído na data do evento ou posterior"
    );
    expect(completeBtn).toBeDisabled();
  });

  it("renders reopen button when wedding status is CANCELED", async () => {
    const onReopenClick = vi.fn();
    const canceledWedding = createMockWedding({
      ...mockWedding,
      status: "CANCELED",
      allowed_transitions: ["IN_PROGRESS"],
    });

    render(
      <WeddingHeader
        wedding={canceledWedding}
        displayDate="15 Set 2026"
        checklistPercentage={30}
        onEditClick={vi.fn()}
        onReopenClick={onReopenClick}
      />
    );

    const reopenBtn = screen.getByTitle("Reabrir casamento");
    expect(reopenBtn).toBeInTheDocument();
    await userEvent.click(reopenBtn);

    expect(onReopenClick).toHaveBeenCalledTimes(1);
  });

  it("renders reopen button when allowed_transitions includes IN_PROGRESS", async () => {
    const onReopenClick = vi.fn();
    const weddingWithReopen = createMockWedding({
      ...mockWedding,
      status: "COMPLETED",
      allowed_transitions: ["IN_PROGRESS"],
    });

    render(
      <WeddingHeader
        wedding={weddingWithReopen}
        displayDate="15 Set 2026"
        checklistPercentage={100}
        onEditClick={vi.fn()}
        onReopenClick={onReopenClick}
      />
    );

    const reopenBtn = screen.getByTitle("Reabrir casamento");
    expect(reopenBtn).toBeInTheDocument();
  });

  it("does not render reopen button when not canceled and allowed_transitions lacks IN_PROGRESS", () => {
    const closedWedding = createMockWedding({
      ...mockWedding,
      status: "COMPLETED",
      allowed_transitions: [],
    });

    render(
      <WeddingHeader
        wedding={closedWedding}
        displayDate="15 Set 2026"
        checklistPercentage={100}
        onEditClick={vi.fn()}
      />
    );

    expect(screen.queryByTitle("Reabrir casamento")).not.toBeInTheDocument();
  });
});
