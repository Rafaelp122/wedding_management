import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { getApiErrorInfo } from "@/api/error-utils";
import {
  useFinancesBudgetsForWedding,
  useFinancesBudgetsPartialUpdate,
  useFinancesCategoriesList,
} from "@/api/generated/v1/endpoints/finances/finances";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { WeddingBudgetCategoriesCard } from "./WeddingBudgetCategoriesCard";
import { WeddingBudgetNotesCard } from "./WeddingBudgetNotesCard";
import { WeddingBudgetSummaryCard } from "./WeddingBudgetSummaryCard";

interface WeddingBudgetProps {
  weddingUuid: string;
}

export function WeddingBudget({ weddingUuid }: WeddingBudgetProps) {
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

  if (isLoadingBudget || isLoadingCategories) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (budgetError || !budget) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>Erro ao carregar orçamento do casamento.</AlertDescription>
      </Alert>
    );
  }

  const totalAllocated = categories.reduce(
    (acc, category) => acc + Number(category.allocated_budget || 0),
    0,
  );
  const totalSpent = Number(budget.total_overall_spent || 0);
  const totalEstimated = Number(budget.total_estimated || 0);

  const progressPercentage =
    totalEstimated > 0 ? (totalSpent / totalEstimated) * 100 : 0;
  const progressColor =
    progressPercentage > 100
      ? "bg-red-500"
      : progressPercentage > 80
        ? "bg-yellow-500"
        : "bg-green-500";

  return (
    <div className="space-y-6">
      <WeddingBudgetSummaryCard
        isEditing={isEditing}
        editTotal={editTotal}
        isSaving={updateBudgetMutation.isPending}
        totalEstimated={totalEstimated}
        totalAllocated={totalAllocated}
        totalSpent={totalSpent}
        progressPercentage={progressPercentage}
        progressColor={progressColor}
        onEditTotalChange={setEditTotal}
        onStartEdit={handleEditInit}
        onSave={handleSave}
        onCancelEdit={() => setIsEditing(false)}
      />

      <WeddingBudgetCategoriesCard categories={categories} />

      {budget.notes && <WeddingBudgetNotesCard notes={budget.notes} />}
    </div>
  );
}
