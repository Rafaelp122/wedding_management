import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { RecentWeddings } from "@/features/dashboard/components/RecentWeddings";
import { createMockWedding } from "@/test-data";

describe("RecentWeddings", () => {
  it("shows empty state when no weddings", () => {
    render(<RecentWeddings weddings={[]} />);

    expect(
      screen.getByText(/nenhum casamento encontrado/i),
    ).toBeInTheDocument();
  });

  it("renders wedding names", () => {
    const weddings = [
      createMockWedding({ uuid: "w-1", groom_name: "João", bride_name: "Maria", status: "IN_PROGRESS" }),
      createMockWedding({ uuid: "w-2", groom_name: "Pedro", bride_name: "Ana", status: "COMPLETED" }),
    ];

    render(<RecentWeddings weddings={weddings} />);

    expect(screen.getByText(/João & Maria/)).toBeInTheDocument();
    expect(screen.getByText(/Pedro & Ana/)).toBeInTheDocument();
  });

  it("shows status labels", () => {
    render(
      <RecentWeddings
        weddings={[createMockWedding({ status: "COMPLETED" })]}
      />,
    );

    expect(screen.getByText("Concluído")).toBeInTheDocument();
  });

  it("shows custom title", () => {
    render(
      <RecentWeddings
        weddings={[createMockWedding()]}
        title="Custom Title"
      />,
    );

    expect(screen.getByText("Custom Title")).toBeInTheDocument();
  });

  it("renders links to wedding detail", () => {
    render(
      <RecentWeddings
        weddings={[createMockWedding({ uuid: "w-123" })]}
      />,
    );

    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/weddings/w-123");
  });
});
