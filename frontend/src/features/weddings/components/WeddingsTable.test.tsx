import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingsTable } from "@/features/weddings/components/WeddingsTable";
import { createMockWedding } from "@/test-data";

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

const mockWeddings = [
  createMockWedding({ uuid: "w-1", groom_name: "João", bride_name: "Maria", status: "IN_PROGRESS" }),
  createMockWedding({ uuid: "w-2", groom_name: "Pedro", bride_name: "Ana", location: "Rio de Janeiro", expected_guests: null, status: "COMPLETED" }),
];

describe("WeddingsTable", () => {
  it("renders wedding rows", () => {
    render(
      <WeddingsTable weddings={mockWeddings} onRefetch={vi.fn()} />,
    );

    expect(screen.getByText(/João & Maria/)).toBeInTheDocument();
    expect(screen.getByText(/Pedro & Ana/)).toBeInTheDocument();
    expect(screen.getByText("São Paulo")).toBeInTheDocument();
    expect(screen.getByText("Rio de Janeiro")).toBeInTheDocument();
  });

  it("shows dash for null expected_guests", () => {
    render(
      <WeddingsTable
        weddings={[createMockWedding({ expected_guests: null })]}
        onRefetch={vi.fn()}
      />,
    );

    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("renders status badge", () => {
    render(
      <WeddingsTable weddings={mockWeddings} onRefetch={vi.fn()} />,
    );

    expect(screen.getByText("Em Andamento")).toBeInTheDocument();
    expect(screen.getByText("Concluído")).toBeInTheDocument();
  });

  it("renders action buttons per row", () => {
    render(
      <WeddingsTable weddings={mockWeddings} onRefetch={vi.fn()} />,
    );

    const actionButtons = screen.getAllByRole("button", { name: /abrir menu/i });
    expect(actionButtons).toHaveLength(2);
  });
});
