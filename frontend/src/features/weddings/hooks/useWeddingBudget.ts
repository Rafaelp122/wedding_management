import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { getApiErrorInfo } from "@/api/error-utils";
import {
  useFinancesBudgetsForWedding,
  useFinancesBudgetsPartialUpdate,
  useFinancesCategoriesList,
} from "@/api/generated/v1/endpoints/finances/finances";

export function useWeddingBudget(weddingUuid: string) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTotal, setEditTotal] = useState<string>("");
  const queryClient = useQueryClient();

  const {
    data: budgetResponse,
    isLoading: isLoadingBudget,
    error: budgetError,
  } = useFinancesBudgetsForWedding(weddingUuid);

  const { data: categoriesResponse, isLoading: isLoadingCategories } =
    useFinancesCategoriesList({ wedding_id: weddingUuid });

  const updateBudgetMutation = useFinancesBudgetsPartialUpdate();

  const budget = budgetResponse?.data;
  const categories = categoriesResponse?.data?.items || [];

  const isLoading = isLoadingBudget || isLoadingCategories;

  const totalAllocated = categories.reduce(
    (acc, category) => acc + Number(category.allocated_budget || 0),
    0,
  );
  const totalSpent = Number(budget?.total_overall_spent || 0);
  const totalEstimated = Number(budget?.total_estimated || 0);

  const progressPercentage =
    totalEstimated > 0 ? (totalSpent / totalEstimated) * 100 : 0;
  const progressColor =
    progressPercentage > 100
      ? "bg-red-500"
      : progressPercentage > 80
        ? "bg-yellow-500"
        : "bg-green-500";

  const handleEditInit = () => {
    if (budget) {
      setEditTotal(budget.total_estimated?.toString() || "0");
      setIsEditing(true);
    }
  };

  const handleSave = async () => {
    if (!budget) return;
    try {
      await updateBudgetMutation.mutateAsync({
        uuid: budget.uuid,
        data: {
          total_estimated: editTotal,
        },
      });
      toast.success("Orçamento atualizado com sucesso!");
      setIsEditing(false);
      queryClient.invalidateQueries();
    } catch (error) {
      const { message } = getApiErrorInfo(
        error,
        "Falha ao atualizar orçamento.",
      );
      toast.error(message);
    }
  };

  const handleCancelEdit = () => setIsEditing(false);

  return {
    budget,
    categories,
    isLoading,
    budgetError,
    isEditing,
    editTotal,
    isSaving: updateBudgetMutation.isPending,
    totalEstimated,
    totalAllocated,
    totalSpent,
    progressPercentage,
    progressColor,
    setEditTotal,
    handleEditInit,
    handleSave,
    handleCancelEdit,
  };
}
