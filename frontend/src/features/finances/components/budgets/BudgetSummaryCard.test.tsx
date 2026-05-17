import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingBudgetSummaryCard } from "./BudgetSummaryCard";

describe("WeddingBudgetSummaryCard", () => {
  const defaultProps = {
    isEditing: false,
    editTotal: "",
    isSaving: false,
    totalEstimated: 30000,
    totalAllocated: 25000,
    totalSpent: 15000,
    progressPercentage: 60,
    progressColor: "bg-blue-500",
    onEditTotalChange: vi.fn(),
    onStartEdit: vi.fn(),
    onSave: vi.fn(),
    onCancelEdit: vi.fn(),
  };

  describe("view mode", () => {
    it("renders card title and description", () => {
      render(<WeddingBudgetSummaryCard {...defaultProps} />);

      expect(screen.getByText("Orçamento Total")).toBeInTheDocument();
      expect(
        screen.getByText(
          /Tabela de gastos planejados e alocados do evento/i,
        ),
      ).toBeInTheDocument();
    });

    it("renders estimated total value formatted in BRL", () => {
      render(<WeddingBudgetSummaryCard {...defaultProps} />);

      expect(screen.getByText("Teto Estimado")).toBeInTheDocument();
      expect(screen.getByText("R$ 30.000,00")).toBeInTheDocument();
    });

    it("renders allocated total value formatted in BRL", () => {
      render(<WeddingBudgetSummaryCard {...defaultProps} />);

      expect(screen.getByText("Total Alocado")).toBeInTheDocument();
      expect(screen.getByText("R$ 25.000,00")).toBeInTheDocument();
    });

    it("renders spent status with progress bar", () => {
      render(<WeddingBudgetSummaryCard {...defaultProps} />);

      expect(screen.getByText("Status de Gastos")).toBeInTheDocument();
      // The spent value is in a single text node
      expect(
        screen.getByText(/R\$ 15\.000,00/),
      ).toBeInTheDocument();
      // The percentage is split across text nodes (60.0 and %) so use a function matcher
      expect(
        screen.getByText((content) => content.includes("60.0")),
      ).toBeInTheDocument();
    });

    it("renders progress bar with correct width", () => {
      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          progressPercentage={45.3}
        />,
      );

      const progressBar = document.querySelector(".bg-blue-500");
      expect(progressBar).toBeInTheDocument();
      expect(progressBar).toHaveStyle({ width: "45.3%" });
    });

    it("caps progress bar width at 100%", () => {
      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          progressPercentage={150}
        />,
      );

      const progressBar = document.querySelector(".bg-blue-500");
      expect(progressBar).toHaveStyle({ width: "100%" });
    });

    it("shows 'Editar Teto' button", () => {
      render(<WeddingBudgetSummaryCard {...defaultProps} />);

      expect(
        screen.getByRole("button", { name: /editar teto/i }),
      ).toBeInTheDocument();
    });

    it("calls onStartEdit when edit button is clicked", async () => {
      const onStartEdit = vi.fn();
      const user = userEvent.setup();

      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          onStartEdit={onStartEdit}
        />,
      );

      await user.click(
        screen.getByRole("button", { name: /editar teto/i }),
      );
      expect(onStartEdit).toHaveBeenCalledTimes(1);
    });

    it("does not render edit form in view mode", () => {
      render(<WeddingBudgetSummaryCard {...defaultProps} />);

      expect(
        screen.queryByLabelText(/novo valor estimado/i),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: /salvar/i }),
      ).not.toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: /cancelar/i }),
      ).not.toBeInTheDocument();
    });
  });

  describe("edit mode", () => {
    it("renders input with current editTotal value", () => {
      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          isEditing={true}
          editTotal="35000"
        />,
      );

      expect(
        screen.getByLabelText(/novo valor estimado/i),
      ).toBeInTheDocument();
      expect(screen.getByDisplayValue("35000")).toBeInTheDocument();
    });

    it("renders save button", () => {
      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          isEditing={true}
        />,
      );

      expect(
        screen.getByRole("button", { name: /salvar/i }),
      ).toBeInTheDocument();
    });

    it("renders cancel button", () => {
      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          isEditing={true}
        />,
      );

      expect(
        screen.getByRole("button", { name: /cancelar/i }),
      ).toBeInTheDocument();
    });

    it("calls onEditTotalChange when input value changes", async () => {
      const onEditTotalChange = vi.fn();
      const user = userEvent.setup();

      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          isEditing={true}
          editTotal="30000"
          onEditTotalChange={onEditTotalChange}
        />,
      );

      const input = screen.getByLabelText(/novo valor estimado/i);
      await user.clear(input);
      await user.type(input, "40000");

      expect(onEditTotalChange).toHaveBeenCalled();
    });

    it("calls onSave when save button is clicked", async () => {
      const onSave = vi.fn();
      const user = userEvent.setup();

      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          isEditing={true}
          onSave={onSave}
        />,
      );

      await user.click(
        screen.getByRole("button", { name: /salvar/i }),
      );
      expect(onSave).toHaveBeenCalledTimes(1);
    });

    it("calls onCancelEdit when cancel button is clicked", async () => {
      const onCancelEdit = vi.fn();
      const user = userEvent.setup();

      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          isEditing={true}
          onCancelEdit={onCancelEdit}
        />,
      );

      await user.click(
        screen.getByRole("button", { name: /cancelar/i }),
      );
      expect(onCancelEdit).toHaveBeenCalledTimes(1);
    });

    it('disables save button and shows "Salvando..." when isSaving is true', () => {
      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          isEditing={true}
          isSaving={true}
        />,
      );

      const saveButton = screen.getByRole("button", {
        name: /salvando/i,
      });
      expect(saveButton).toBeDisabled();
    });

    it("does not show 'Editar Teto' button in edit mode", () => {
      render(
        <WeddingBudgetSummaryCard
          {...defaultProps}
          isEditing={true}
        />,
      );

      expect(
        screen.queryByRole("button", { name: /editar teto/i }),
      ).not.toBeInTheDocument();
    });
  });
});
