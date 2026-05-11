import { toast } from "sonner";
import { useFinancesExpensesDelete } from "@/api/generated/v1/endpoints/finances/finances";
import { getApiErrorInfo } from "@/api/error-utils";
import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";
import { ConfirmDeleteDialog } from "@/components/ui/confirm-delete-dialog";

interface DeleteExpenseDialogProps {
  expense: ExpenseOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function DeleteExpenseDialog({
  expense,
  open,
  onOpenChange,
  onSuccess,
}: DeleteExpenseDialogProps) {
  const { mutate, isPending } = useFinancesExpensesDelete();
  const expenseName = expense.name || expense.description || expense.uuid;

  const handleConfirm = () => {
    mutate(
      { uuid: expense.uuid },
      {
        onSuccess: () => {
          toast.success("Despesa deletada com sucesso!");
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao deletar despesa.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <ConfirmDeleteDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Deletar Despesa"
      description="Esta ação não pode ser desfeita. Todas as parcelas vinculadas serão permanentemente removidas."
      itemName={expenseName}
      consequences={[
        "Todas as parcelas (pagas ou pendentes) serão removidas",
        "Se precisar apenas corrigir o número de parcelas, use a opção \"Editar\"",
      ]}
      requireTypedConfirmation
      onConfirm={handleConfirm}
      isPending={isPending}
    />
  );
}
