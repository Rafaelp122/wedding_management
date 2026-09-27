import { memo } from "react";
import { AlertCircle, Loader2 } from "lucide-react";

import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

export interface CancelContractDialogViewProps {
  contract: ContractOut | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  isPending: boolean;
}

export const CancelContractDialogView = memo(function CancelContractDialogView({
  contract,
  open,
  onOpenChange,
  onConfirm,
  isPending,
}: CancelContractDialogViewProps) {
  const contractName =
    contract?.name || contract?.description || contract?.supplier_name || "este contrato";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[460px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertCircle className="size-5" />
            Cancelar Contrato
          </DialogTitle>
          <DialogDescription>
            Tem certeza de que deseja distratar e cancelar <strong>{contractName}</strong>?
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-2 text-xs text-muted-foreground leading-relaxed">
          <p>
            O status do contrato será alterado para <strong>Cancelado</strong>.
          </p>
          <ul className="list-disc pl-4 space-y-1">
            <li>Os itens logísticos vinculados permanecerão associados com histórico.</li>
            <li>Qualquer despesa financeira continuará registrada, mas vinculada ao contrato cancelado.</li>
          </ul>
        </div>

        <DialogFooter className="gap-2 sm:gap-0 mt-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isPending}
          >
            Voltar
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={onConfirm}
            disabled={isPending || !contract}
          >
            {isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Cancelando...
              </>
            ) : (
              "Confirmar Cancelamento"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
});
