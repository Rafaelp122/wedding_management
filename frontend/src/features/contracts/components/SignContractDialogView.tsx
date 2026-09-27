import { memo, useState } from "react";
import { CheckCircle, Loader2 } from "lucide-react";

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

export interface SignContractDialogViewProps {
  contract: ContractOut | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (signedDate: string) => void;
  isPending: boolean;
}

export const SignContractDialogView = memo(function SignContractDialogView({
  contract,
  open,
  onOpenChange,
  onConfirm,
  isPending,
}: SignContractDialogViewProps) {
  const todayStr = new Date().toISOString().slice(0, 10);
  const [signedDate, setSignedDate] = useState<string>(todayStr);

  const contractName =
    contract?.name || contract?.description || contract?.supplier_name || "este contrato";

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
            onClick={() => onConfirm(signedDate || todayStr)}
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
