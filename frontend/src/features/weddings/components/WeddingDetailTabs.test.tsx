import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingDetailTabs } from "@/features/weddings/components/WeddingDetailTabs";
import { createMockWedding } from "@/test-data";

const mockWedding = createMockWedding({ groom_name: "João", bride_name: "Maria" });

describe("WeddingDetailTabs", () => {
  it("renders tab triggers", () => {
    render(<WeddingDetailTabs wedding={mockWedding} />);

    expect(screen.getByRole("tab", { name: /geral/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /finanças/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /logística/i })).toBeInTheDocument();
    expect(
      screen.getByRole("tab", { name: /planejamento/i }),
    ).toBeInTheDocument();
  });

  it("shows general tab content area", () => {
    render(<WeddingDetailTabs wedding={mockWedding} />);

    expect(screen.getByText("Geral")).toBeInTheDocument();
  });
});
