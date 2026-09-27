import { memo, useState } from "react";
import { CheckCircle, Loader2 } from "lucide-react";

import type { ContractAddendumOut } from "@/api/generated/v1/models/contractAddendumOut";
import { formatCurrencyBR } from "@/lib/formatters";
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

export interface SignAddendumDialogViewProps {
  addendum: ContractAddendumOut | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (signedDate: string) => void;
  isPending: boolean;
}

export const SignAddendumDialogView = memo(function SignAddendumDialogView({
  addendum,
  open,
  onOpenChange,
  onConfirm,
  isPending,
}: SignAddendumDialogViewProps) {
  const todayStr = new Date().toISOString().slice(0, 10);
  const [signedDate, setSignedDate] = useState<string>(todayStr);

  const formattedAmount = addendum
    ? `R$ ${formatCurrencyBR(Number(addendum.amount))}`
    : "";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[460px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-primary">
            <CheckCircle className="size-5" />
            Formalizar Assinatura do Aditivo
          </DialogTitle>
          <DialogDescription>
            Confirme a assinatura deste aditivo no valor de{" "}
            <strong>{formattedAmount}</strong>.
            {addendum?.justification && (
              <span className="block mt-1 italic text-muted-foreground">
                &ldquo;{addendum.justification}&rdquo;
              </span>
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label htmlFor="addendum-signed-date" className="text-sm font-medium">
              Data da Assinatura
            </Label>
            <Input
              id="addendum-signed-date"
              type="date"
              value={signedDate}
              onChange={(e) => setSignedDate(e.target.value)}
              disabled={isPending}
            />
          </div>

          <p className="text-xs text-muted-foreground leading-relaxed">
            Ao assinar, o status do aditivo passará para <strong>Assinado</strong>{" "}
            e o valor efetivo do contrato principal será atualizado pelo backend.
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
            disabled={isPending || !addendum}
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
