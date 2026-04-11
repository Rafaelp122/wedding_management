import type { SupplierOut } from "@/api/generated/v1/models";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface DeleteSupplierDialogProps {
  supplier: SupplierOut | null;
  isDeleting: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}

export function DeleteSupplierDialog({
  supplier,
  isDeleting,
  onCancel,
  onConfirm,
}: DeleteSupplierDialogProps) {
  return (
    <Dialog open={!!supplier} onOpenChange={(open) => !open && onCancel()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Excluir fornecedor</DialogTitle>
          <DialogDescription>Esta ação não pode ser desfeita.</DialogDescription>
        </DialogHeader>

        <p className="text-sm text-muted-foreground">
          Deseja realmente excluir{" "}
          <span className="font-semibold text-foreground">{supplier?.name}</span>?
        </p>

        <DialogFooter>
          <Button variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
          <Button variant="destructive" onClick={onConfirm} disabled={isDeleting}>
            {isDeleting ? "Excluindo..." : "Excluir"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
