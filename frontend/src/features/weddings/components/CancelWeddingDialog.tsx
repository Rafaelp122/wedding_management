import { memo } from "react";
import { toast } from "sonner";
import { AlertCircle, Loader2 } from "lucide-react";
import { useWeddingsCancel } from "@/api/generated/v1/endpoints/weddings/weddings";
import { getApiErrorInfo } from "@/api/error-utils";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface CancelWeddingDialogProps {
  wedding: WeddingOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const CancelWeddingDialog = memo(function CancelWeddingDialog({
  wedding,
  open,
  onOpenChange,
  onSuccess,
}: CancelWeddingDialogProps) {
  const { mutate, isPending } = useWeddingsCancel();
  const weddingName = `${wedding.groom_name} & ${wedding.bride_name}`;

  const handleConfirm = () => {
    mutate(
      { uuid: wedding.uuid },
      {
        onSuccess: () => {
          toast.success("Casamento cancelado com sucesso!");
          onOpenChange(false);
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao cancelar casamento.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[460px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertCircle className="size-5" />
            Cancelar Casamento
          </DialogTitle>
          <DialogDescription>
            Tem certeza de que deseja cancelar o casamento de <strong>{weddingName}</strong>?
          </DialogDescription>
        </DialogHeader>

        <p className="text-xs text-muted-foreground leading-relaxed">
          O status do casamento será alterado para <strong>Cancelado</strong>. As notificações e efeitos colaterais de encerramento serão processados automaticamente.
        </p>

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
            onClick={handleConfirm}
            disabled={isPending}
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
