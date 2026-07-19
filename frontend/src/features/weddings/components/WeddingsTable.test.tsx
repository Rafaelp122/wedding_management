import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingsTable } from "@/features/weddings/components/WeddingsTable";
import { createMockWedding } from "@/test-data";

const mockWeddings = [
  createMockWedding({
    uuid: "w-1",
    groom_name: "João",
    bride_name: "Maria",
    status: "IN_PROGRESS",
    expected_guests: 150,
    total_budget: 50000,
    overdue_installments: 1,
    incomplete_tasks: 2,
  }),
  createMockWedding({
    uuid: "w-2",
    groom_name: "Pedro",
    bride_name: "Ana",
    location: "Rio de Janeiro",
    expected_guests: null,
    status: "COMPLETED",
    total_budget: null,
    overdue_installments: 0,
    incomplete_tasks: 0,
  }),
];

const PAGE_SIZE = 10;

describe("WeddingsTable", () => {
  it("renders wedding rows with names and locations", () => {
    render(
      <WeddingsTable
        weddings={mockWeddings}
        pageSize={PAGE_SIZE}
        onWeddingClick={vi.fn()}
        onEditClick={vi.fn()}
        onDeleteClick={vi.fn()}
      />,
    );

    expect(screen.getByText(/João & Maria/)).toBeInTheDocument();
    expect(screen.getByText(/Pedro & Ana/)).toBeInTheDocument();
    expect(screen.getByText("São Paulo")).toBeInTheDocument();
    expect(screen.getByText("Rio de Janeiro")).toBeInTheDocument();
  });

  it("renders status badges", () => {
    render(
      <WeddingsTable
        weddings={mockWeddings}
        pageSize={PAGE_SIZE}
        onWeddingClick={vi.fn()}
        onEditClick={vi.fn()}
        onDeleteClick={vi.fn()}
      />,
    );

    expect(screen.getByText("Em Andamento")).toBeInTheDocument();
    expect(screen.getByText("Concluído")).toBeInTheDocument();
  });

  it("renders Convidados with value or dash", () => {
    render(
      <WeddingsTable
        weddings={mockWeddings}
        pageSize={PAGE_SIZE}
        onWeddingClick={vi.fn()}
        onEditClick={vi.fn()}
        onDeleteClick={vi.fn()}
      />,
    );

    expect(screen.getByText("150")).toBeInTheDocument();
    const dashes = screen.getAllByText("—");
    expect(dashes.length).toBeGreaterThanOrEqual(1);
  });

  it("renders Orçamento formatted or dash", () => {
    const { container } = render(
      <WeddingsTable
        weddings={mockWeddings}
        pageSize={PAGE_SIZE}
        onWeddingClick={vi.fn()}
        onEditClick={vi.fn()}
        onDeleteClick={vi.fn()}
      />,
    );

    expect(container.textContent).toContain("50.000");
  });

  it("renders Pendências with alert icon when > 0", () => {
    render(
      <WeddingsTable
        weddings={mockWeddings}
        pageSize={PAGE_SIZE}
        onWeddingClick={vi.fn()}
        onEditClick={vi.fn()}
        onDeleteClick={vi.fn()}
      />,
    );

    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("renders edit and delete buttons for non-completed weddings", () => {
    render(
      <WeddingsTable
        weddings={mockWeddings}
        pageSize={PAGE_SIZE}
        onWeddingClick={vi.fn()}
        onEditClick={vi.fn()}
        onDeleteClick={vi.fn()}
      />,
    );

    expect(screen.getByTitle("Editar")).toBeInTheDocument();
    expect(screen.getByTitle("Excluir")).toBeInTheDocument();
    expect(screen.getByTitle("Ver Detalhes")).toBeInTheDocument();
  });

  it("renders table columns", () => {
    render(
      <WeddingsTable
        weddings={mockWeddings}
        pageSize={PAGE_SIZE}
        onWeddingClick={vi.fn()}
        onEditClick={vi.fn()}
        onDeleteClick={vi.fn()}
      />,
    );

    expect(screen.getByText("Noivos")).toBeInTheDocument();
    expect(screen.getByText("Data do Evento")).toBeInTheDocument();
    expect(screen.getByText("Status")).toBeInTheDocument();
    expect(screen.getByText("Convidados")).toBeInTheDocument();
    expect(screen.getByText("Orçamento")).toBeInTheDocument();
    expect(screen.getByText("Pendências")).toBeInTheDocument();
  });

  it("renders empty placeholder rows to fill page size", () => {
    const { container } = render(
      <WeddingsTable
        weddings={mockWeddings}
        pageSize={4}
        onWeddingClick={vi.fn()}
        onEditClick={vi.fn()}
        onDeleteClick={vi.fn()}
      />,
    );

    const rows = container.querySelectorAll("tbody tr");
    expect(rows.length).toBe(4);
  });

  it("calls callbacks when clicking rows and action buttons", async () => {
    const onWeddingClick = vi.fn();
    const onEditClick = vi.fn();
    const onDeleteClick = vi.fn();

    render(
      <WeddingsTable
        weddings={mockWeddings}
        pageSize={PAGE_SIZE}
        onWeddingClick={onWeddingClick}
        onEditClick={onEditClick}
        onDeleteClick={onDeleteClick}
      />,
    );

    const rowText = screen.getByText(/João & Maria/);
    await userEvent.click(rowText);
    expect(onWeddingClick).toHaveBeenCalledWith(mockWeddings[0]);

    const editBtn = screen.getByTitle("Editar");
    await userEvent.click(editBtn);
    expect(onEditClick).toHaveBeenCalledWith(mockWeddings[0]);

    const deleteBtn = screen.getByTitle("Excluir");
    await userEvent.click(deleteBtn);
    expect(onDeleteClick).toHaveBeenCalledWith(mockWeddings[0]);
  });
});
