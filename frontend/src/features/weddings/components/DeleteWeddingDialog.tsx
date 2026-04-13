import { useState } from "react";
import { toast } from "sonner";
import { useWeddingsDelete } from "@/api/generated/v1/endpoints/weddings/weddings";
import { getApiErrorInfo } from "@/api/error-utils";
import type { WeddingOut } from "@/api/generated/v1/models";

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

interface DeleteWeddingDialogProps {
  wedding: WeddingOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function DeleteWeddingDialog({
  wedding,
  open,
  onOpenChange,
  onSuccess,
}: DeleteWeddingDialogProps) {
  const [confirmText, setConfirmText] = useState("");
  const { mutate, isPending } = useWeddingsDelete();

  const handleDelete = () => {
    mutate(
      { uuid: wedding.uuid },
      {
        onSuccess: () => {
          toast.success("Casamento deletado com sucesso!");
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Erro ao deletar casamento.",
          );
          toast.error(message);
        },
      },
    );
  };

  const weddingName = `${wedding.groom_name} & ${wedding.bride_name}`;
  const isConfirmed = confirmText === weddingName;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="size-5" />
            Deletar Casamento
          </DialogTitle>
          <DialogDescription>
            Esta ação não pode ser desfeita. Todos os dados relacionados serão
            permanentemente removidos.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          <Alert variant="destructive">
            <AlertDescription>
              <strong>Atenção:</strong> Ao deletar este casamento, os seguintes
              dados também serão removidos:
              <ul className="mt-2 list-disc list-inside flex flex-col gap-1 text-sm">
                <li>Orçamentos e categorias</li>
                <li>Despesas e parcelas</li>
                <li>Contratos vinculados</li>
                <li>Eventos do scheduler</li>
              </ul>
            </AlertDescription>
          </Alert>

          <div className="flex flex-col gap-2">
            <p className="text-sm font-medium">
              Para confirmar, digite o nome do casamento:
            </p>
            <p className="text-sm font-semibold bg-muted p-2 rounded">
              {weddingName}
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
