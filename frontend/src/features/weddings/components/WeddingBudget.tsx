import { AlertCircle } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { useWeddingBudget } from "../hooks/useWeddingBudget";
import { WeddingBudgetCategoriesCard } from "./WeddingBudgetCategoriesCard";
import { WeddingBudgetNotesCard } from "./WeddingBudgetNotesCard";
import { WeddingBudgetSummaryCard } from "./WeddingBudgetSummaryCard";

interface WeddingBudgetProps {
  weddingUuid: string;
}

export function WeddingBudget({ weddingUuid }: WeddingBudgetProps) {
  const {
    budget,
    categories,
    isLoading,
    budgetError,
    isEditing,
    editTotal,
    isSaving,
    totalEstimated,
    totalAllocated,
    totalSpent,
    progressPercentage,
    progressColor,
    setEditTotal,
    handleEditInit,
    handleSave,
    handleCancelEdit,
  } = useWeddingBudget(weddingUuid);

  if (isLoading) {
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

  return (
    <div className="space-y-6">
      <WeddingBudgetSummaryCard
        isEditing={isEditing}
        editTotal={editTotal}
        isSaving={isSaving}
        totalEstimated={totalEstimated}
        totalAllocated={totalAllocated}
        totalSpent={totalSpent}
        progressPercentage={progressPercentage}
        progressColor={progressColor}
        onEditTotalChange={setEditTotal}
        onStartEdit={handleEditInit}
        onSave={handleSave}
        onCancelEdit={handleCancelEdit}
      />

      <WeddingBudgetCategoriesCard categories={categories} />

      {budget.notes && <WeddingBudgetNotesCard notes={budget.notes} />}
    </div>
  );
}
