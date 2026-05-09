import { toast } from "sonner";

import { useFinancesCategoriesDelete } from "@/api/generated/v1/endpoints/finances/finances";
import { getApiErrorInfo } from "@/api/error-utils";
import type { BudgetCategoryOut } from "@/api/generated/v1/models/budgetCategoryOut";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Loader2, AlertCircle } from "lucide-react";

interface DeleteBudgetCategoryDialogProps {
  category: BudgetCategoryOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function DeleteBudgetCategoryDialog({
  category,
  open,
  onOpenChange,
  onSuccess,
}: DeleteBudgetCategoryDialogProps) {
  const { mutate, isPending } = useFinancesCategoriesDelete();

  const hasExpenses = parseFloat(category.total_spent ?? "0") > 0;

  const handleDelete = () => {
    mutate(
      { uuid: category.uuid },
      {
        onSuccess: () => {
          toast.success("Categoria removida com sucesso!");
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Falha ao remover categoria.",
          );
          toast.error(message);
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Remover Categoria</DialogTitle>
          <DialogDescription>
            Tem certeza que deseja remover a categoria{" "}
            <strong>{category.name}</strong>?
          </DialogDescription>
        </DialogHeader>

        {hasExpenses ? (
          <div className="flex items-start gap-2 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
            <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
            <span>
              Esta categoria possui R${" "}
              {parseFloat(category.total_spent ?? "0").toLocaleString(
                "pt-BR",
                { minimumFractionDigits: 2 },
              )}{" "}
              em despesas vinculadas. Remova as despesas antes de excluir a
              categoria.
            </span>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Esta ação é irreversível. Todos os dados desta categoria serão
            permanentemente removidos.
          </p>
        )}

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isPending}
          >
            Cancelar
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleDelete}
            disabled={isPending || hasExpenses}
          >
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Remover
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
