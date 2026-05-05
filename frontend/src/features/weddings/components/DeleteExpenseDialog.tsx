import { useState } from "react";
import { toast } from "sonner";
import { useFinancesExpensesDelete } from "@/api/generated/v1/endpoints/finances/finances";
import { getApiErrorInfo } from "@/api/error-utils";
import type { ExpenseOut } from "@/api/generated/v1/models";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Loader2, AlertTriangle } from "lucide-react";

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
  const [confirmText, setConfirmText] = useState("");
  const { mutate, isPending } = useFinancesExpensesDelete();

  const handleDelete = () => {
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

  const expenseName = expense.name || expense.description || expense.uuid;
  const isConfirmed = confirmText === expenseName;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="size-5" />
            Deletar Despesa
          </DialogTitle>
          <DialogDescription>
            Esta ação não pode ser desfeita. Todas as parcelas vinculadas serão
            permanentemente removidas.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          <Alert variant="destructive">
            <AlertDescription>
              <ul className="list-disc list-inside flex flex-col gap-1 text-sm">
                <li>Todas as parcelas (pagas ou pendentes) serão removidas</li>
                <li>
                  Se precisar apenas corrigir o número de parcelas, use a opção
                  "Editar"
                </li>
              </ul>
            </AlertDescription>
          </Alert>

          <div className="flex flex-col gap-2">
            <p className="text-sm font-medium">
              Para confirmar, digite o nome da despesa:
            </p>
            <p className="text-sm font-semibold bg-muted p-2 rounded">
              {expenseName}
            </p>
            <Input
              type="text"
              placeholder="Digite o nome aqui..."
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              disabled={isPending}
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => {
              setConfirmText("");
              onOpenChange(false);
            }}
            disabled={isPending}
          >
            Cancelar
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={!isConfirmed || isPending}
          >
            {isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
            Deletar Permanentemente
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
