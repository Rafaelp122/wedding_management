import { memo, useState } from "react";
import { toast } from "sonner";
import { CheckCircle, Loader2 } from "lucide-react";

import { useLogisticsContractsSign } from "@/api/generated/v1/endpoints/logistics/logistics";
import { getApiErrorInfo } from "@/api/error-utils";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface SignContractDialogProps {
  contract: ContractOut | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const SignContractDialog = memo(function SignContractDialog({
  contract,
  open,
  onOpenChange,
  onSuccess,
}: SignContractDialogProps) {
  const { mutate, isPending } = useLogisticsContractsSign();
  const todayStr = new Date().toISOString().slice(0, 10);
  const [signedDate, setSignedDate] = useState<string>(todayStr);

  const contractName =
    contract?.name || contract?.description || contract?.supplier_name || "este contrato";

  const handleConfirm = () => {
    if (!contract) return;
    mutate(
      {
        uuid: contract.uuid,
        data: {
          signed_date: signedDate || todayStr,
        },
      },
      {
        onSuccess: () => {
          toast.success("Contrato assinado formalmente com sucesso!");
          onOpenChange(false);
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao formalizar assinatura do contrato.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[460px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-primary">
            <CheckCircle className="size-5" />
            Formalizar Assinatura
          </DialogTitle>
          <DialogDescription>
            Confirme a formalização e assinatura de <strong>{contractName}</strong>.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="signed-date" className="text-sm font-medium">
              Data da Assinatura
            </Label>
            <Input
              id="signed-date"
              type="date"
              value={signedDate}
              onChange={(e) => setSignedDate(e.target.value)}
              disabled={isPending}
            />
          </div>

          <p className="text-xs text-muted-foreground leading-relaxed">
            Ao assinar, o status do contrato passará para <strong>Assinado</strong>.
            Certifique-se de que o documento físico/digital foi anexado previamente caso exigido.
          </p>
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
            onClick={handleConfirm}
            disabled={isPending || !contract}
          >
            {isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Assinando...
              </>
            ) : (
              "Confirmar Assinatura"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
});
