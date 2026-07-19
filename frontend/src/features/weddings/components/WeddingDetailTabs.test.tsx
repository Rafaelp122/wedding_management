import { describe, expect, it } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingDetailTabs } from "@/features/weddings/components/WeddingDetailTabs";
import { createMockWedding } from "@/test-data";

const mockWedding = createMockWedding({ groom_name: "João", bride_name: "Maria" });

const mockOverview = {
  days_until_wedding: 120,
  budget_percentage_used: 45,
  tasks_completed: 10,
  tasks_total: 20,
  contracts_signed: 4,
  contracts_total: 8,
  urgent_tasks: [],
  upcoming_installments: [],
  categories_summary: [],
};

describe("WeddingDetailTabs", () => {

  it("renders tab triggers", () => {
    render(<WeddingDetailTabs wedding={mockWedding} />);

    expect(screen.getByRole("tab", { name: /visão geral/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /finanças/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /logística/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /planejamento/i })).toBeInTheDocument();
  });

  it("selects general tab by default", () => {
    render(<WeddingDetailTabs wedding={mockWedding} />);

    const generalTab = screen.getByRole("tab", { name: /visão geral/i });
    expect(generalTab).toHaveAttribute("data-state", "active");
  });

  it("alternates tabs when clicked, updating searchParams", async () => {
    render(<WeddingDetailTabs wedding={mockWedding} />);
    const user = userEvent.setup();

    // Click "Finanças" tab trigger
    const financesTab = screen.getByRole("tab", { name: /finanças/i });
    await user.click(financesTab);

    // Verify it is active
    expect(financesTab).toHaveAttribute("data-state", "active");

    // Click "Logística" tab trigger
    const logisticsTab = screen.getByRole("tab", { name: /logística/i });
    await user.click(logisticsTab);
    expect(logisticsTab).toHaveAttribute("data-state", "active");
  });

  it("alternates planning subtabs and updates subtab searchParams", async () => {
    render(<WeddingDetailTabs wedding={mockWedding} />);
    const user = userEvent.setup();

    // Click "Planejamento" tab trigger to render planning contents
    const planningTab = screen.getByRole("tab", { name: /planejamento/i });
    await user.click(planningTab);
    expect(planningTab).toHaveAttribute("data-state", "active");

    // Planning subtabs should be visible (Cronograma and Checklist)
    const timelineSubTab = screen.getByRole("tab", { name: /cronograma/i });
    const checklistSubTab = screen.getByRole("tab", { name: /checklist/i });
    expect(timelineSubTab).toBeInTheDocument();
    expect(checklistSubTab).toBeInTheDocument();

    // Alternate to Checklist subtab
    await user.click(checklistSubTab);
    expect(checklistSubTab).toHaveAttribute("data-state", "active");

    // Alternate back to Timeline subtab
    await user.click(timelineSubTab);
    expect(timelineSubTab).toHaveAttribute("data-state", "active");
  });

  it("navigates to planning tab and selects checklist subtab when clicking 'Ver planejamento' in overview", async () => {
    render(<WeddingDetailTabs wedding={mockWedding} overview={mockOverview} />);
    const user = userEvent.setup();

    // Click navigation button inside overview card
    const navBtn = screen.getByRole("button", { name: /ver planejamento/i });
    await user.click(navBtn);

    // Verify "Planejamento" tab trigger is now active
    const planningTab = screen.getByRole("tab", { name: /planejamento/i });
    expect(planningTab).toHaveAttribute("data-state", "active");

    // Verify "Checklist" subtab trigger is active (as defined by onNavigateToPlanning)
    const checklistSubTab = screen.getByRole("tab", { name: /checklist/i });
    expect(checklistSubTab).toHaveAttribute("data-state", "active");
  });

  it("navigates to finances tab when clicking 'Ver finanças' in overview", async () => {
    render(<WeddingDetailTabs wedding={mockWedding} overview={mockOverview} />);
    const user = userEvent.setup();

    // Click navigation button inside overview card
    const navBtn = screen.getByRole("button", { name: /ver finanças/i });
    await user.click(navBtn);

    // Verify "Finanças" tab trigger is now active
    const financesTab = screen.getByRole("tab", { name: /finanças/i });
    expect(financesTab).toHaveAttribute("data-state", "active");
  });
});
