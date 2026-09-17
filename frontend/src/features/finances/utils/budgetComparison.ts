/**
 * Utilitário puro para cálculo e comparação do orçamento de um casamento
 * em relação à média geral dos casamentos do tenant (ADR-024).
 */

export interface BudgetComparisonInput {
  total_estimated?: string | number | null;
}

export interface BudgetComparisonResult {
  hasEnoughData: boolean;
  diffPercentage: number;
  isBudgetGreater: boolean;
  isBudgetEqual: boolean;
}

export function calculateBudgetComparison(
  currentTotalEstimated: number,
  budgets: BudgetComparisonInput[],
): BudgetComparisonResult {
  const validBudgets = budgets.filter((b) => Number(b.total_estimated || 0) > 0);
  const hasEnoughData = validBudgets.length >= 2;

  if (!hasEnoughData) {
    return {
      hasEnoughData: false,
      diffPercentage: 0,
      isBudgetGreater: false,
      isBudgetEqual: false,
    };
  }

  const totalOfBudgets = validBudgets.reduce(
    (sum, b) => sum + Number(b.total_estimated || 0),
    0,
  );
  const averageBudget = totalOfBudgets / validBudgets.length;

  if (averageBudget <= 0) {
    return {
      hasEnoughData: false,
      diffPercentage: 0,
      isBudgetGreater: false,
      isBudgetEqual: false,
    };
  }

  if (currentTotalEstimated > averageBudget) {
    return {
      hasEnoughData: true,
      diffPercentage: Math.round(
        ((currentTotalEstimated - averageBudget) / averageBudget) * 100,
      ),
      isBudgetGreater: true,
      isBudgetEqual: false,
    };
  }

  if (currentTotalEstimated < averageBudget) {
    return {
      hasEnoughData: true,
      diffPercentage: Math.round(
        ((averageBudget - currentTotalEstimated) / averageBudget) * 100,
      ),
      isBudgetGreater: false,
      isBudgetEqual: false,
    };
  }

  return {
    hasEnoughData: true,
    diffPercentage: 0,
    isBudgetGreater: false,
    isBudgetEqual: true,
  };
}
