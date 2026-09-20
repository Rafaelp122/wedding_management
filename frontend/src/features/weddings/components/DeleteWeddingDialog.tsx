import { toast } from "sonner";
import { useWeddingsDelete } from "@/api/generated/v1/endpoints/weddings/weddings";
import { getApiErrorInfo } from "@/api/error-utils";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import { ConfirmDeleteDialog } from "@/components/ui/confirm-delete-dialog";

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
  const { mutate, isPending } = useWeddingsDelete();
  const weddingName = `${wedding.groom_name} & ${wedding.bride_name}`;

  const handleConfirm = () => {
    mutate(
      { uuid: wedding.uuid },
      {
        onSuccess: () => {
          toast.success("Casamento deletado com sucesso!");
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao deletar casamento.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <ConfirmDeleteDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Deletar Casamento"
      description="Esta ação não pode ser desfeita. Todos os dados relacionados serão permanentemente removidos."
      itemName={weddingName}
      consequences={[
        "Orçamentos e categorias",
        "Eventos do scheduler",
        "Casamentos com contratos ou despesas ativas são protegidos contra exclusão (BR-W03); remova esses vínculos antes de prosseguir",
      ]}
      requireTypedConfirmation
      onConfirm={handleConfirm}
      isPending={isPending}
    />
  );
}
