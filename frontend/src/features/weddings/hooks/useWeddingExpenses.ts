import { useFinancesExpensesList } from "@/api/generated/v1/endpoints/finances/finances";

export function useWeddingExpenses(weddingUuid: string) {
  const {
    data: expensesResponse,
    isLoading,
    error,
  } = useFinancesExpensesList({ event_id: weddingUuid });

  const expenses = expensesResponse?.data?.items || [];

  return {
    expenses,
    isLoading,
    error,
  };
}
