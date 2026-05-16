import { lazy, Suspense, useState } from "react";
import { Plus, Pencil, Trash2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { formatCurrencyBRCompact, parseDecimal } from "@/lib/formatters";
import type { BudgetCategoryOut } from "@/api/generated/v1/models/budgetCategoryOut";

const CreateBudgetCategoryDialog = lazy(
  () =>
    import("./budgets/CreateBudgetCategoryDialog").then((m) => ({
      default: m.CreateBudgetCategoryDialog,
    })),
);
const EditBudgetCategoryDialog = lazy(
  () =>
    import("./budgets/EditBudgetCategoryDialog").then((m) => ({
      default: m.EditBudgetCategoryDialog,
    })),
);
const DeleteBudgetCategoryDialog = lazy(
  () =>
    import("./budgets/DeleteBudgetCategoryDialog").then((m) => ({
      default: m.DeleteBudgetCategoryDialog,
    })),
);

interface WeddingFinancesGroupsSummaryProps {
  categories: BudgetCategoryOut[];
  weddingUuid: string;
  onCategoryChanged?: () => void;
}

export function WeddingFinancesGroupsSummary({
  categories,
  weddingUuid,
  onCategoryChanged,
}: WeddingFinancesGroupsSummaryProps) {
  const [showAll, setShowAll] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<BudgetCategoryOut | null>(null);
  const [deletingCategory, setDeletingCategory] = useState<BudgetCategoryOut | null>(null);

  const displayedCategories = showAll ? categories : categories.slice(0, 5);

  const handleSuccess = () => {
    onCategoryChanged?.();
  };

  return (
    <>
      <Card className="border-none shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-bold">Resumo por Grupo</CardTitle>
            <Button
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0"
              onClick={() => setCreateOpen(true)}
              aria-label="Nova Categoria"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          {displayedCategories.map((category) => {
            const allocatedBudget = parseDecimal(category.allocated_budget);
            const spentAmount = parseDecimal(category.total_spent);
            const percentage =
              allocatedBudget > 0
                ? Math.round((spentAmount / allocatedBudget) * 100)
                : 0;

            return (
              <div key={category.uuid} className="space-y-2">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-1">
                    <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                      {category.name}
                    </span>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 text-muted-foreground hover:text-foreground"
                          aria-label="Opções de categoria"
                        >
                          <span className="text-[10px] font-bold leading-none" aria-hidden>
                            ...
                          </span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="start" className="w-32">
                        <DropdownMenuItem
                          onClick={() => setEditingCategory(category)}
                        >
                          <Pencil className="mr-2 h-3 w-3" />
                          Editar
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => setDeletingCategory(category)}
                        >
                          <Trash2 className="mr-2 h-3 w-3" />
                          Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                  <span className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
                    {formatCurrencyBRCompact(spentAmount)}
                  </span>
                </div>
                <div className="relative h-2 w-full bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                  <div
                    className="absolute top-0 left-0 h-full bg-violet-500 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between text-[10px] text-zinc-400 uppercase font-bold tracking-wider">
                  <span>{percentage}% do teto</span>
                  <span>Teto: {formatCurrencyBRCompact(allocatedBudget)}</span>
                </div>
              </div>
            );
          })}
          {categories.length > 5 && (
            <Button
              variant="outline"
              className="w-full mt-2 text-xs font-bold border-zinc-200 text-zinc-600 hover:bg-zinc-50"
              onClick={() => setShowAll(!showAll)}
            >
              {showAll ? "Mostrar Menos" : "Ver Todas Categorias"}
            </Button>
          )}
        </CardContent>
      </Card>

      <Suspense fallback={null}>
        <CreateBudgetCategoryDialog
          weddingUuid={weddingUuid}
          open={createOpen}
          onOpenChange={setCreateOpen}
          onSuccess={handleSuccess}
        />
      </Suspense>

      {editingCategory && (
        <Suspense fallback={null}>
          <EditBudgetCategoryDialog
            category={editingCategory}
            open={!!editingCategory}
            onOpenChange={(open) => {
              if (!open) setEditingCategory(null);
            }}
            onSuccess={handleSuccess}
          />
        </Suspense>
      )}

      {deletingCategory && (
        <Suspense fallback={null}>
          <DeleteBudgetCategoryDialog
            category={deletingCategory}
            open={!!deletingCategory}
            onOpenChange={(open) => {
              if (!open) setDeletingCategory(null);
            }}
            onSuccess={handleSuccess}
          />
        </Suspense>
      )}
    </>
  );
}
