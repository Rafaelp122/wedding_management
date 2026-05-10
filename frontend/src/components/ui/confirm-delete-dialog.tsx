import { useState, memo, useEffect } from "react";
import { Loader2, AlertTriangle } from "lucide-react";

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

interface ConfirmDeleteDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  itemName: string;
  consequences?: string[];
  requireTypedConfirmation?: boolean;
  onConfirm: () => void;
  isPending?: boolean;
}

export const ConfirmDeleteDialog = memo(function ConfirmDeleteDialog({
  open,
  onOpenChange,
  title,
  description,
  itemName,
  consequences,
  requireTypedConfirmation = false,
  onConfirm,
  isPending = false,
}: ConfirmDeleteDialogProps) {
  const [confirmText, setConfirmText] = useState("");
  const isConfirmed = requireTypedConfirmation ? confirmText === itemName : true;

  useEffect(() => {
    if (open) setConfirmText("");
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="size-5" />
            {title}
          </DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          {consequences && consequences.length > 0 && (
            <Alert variant="destructive">
              <AlertDescription>
                <ul className="list-disc list-inside flex flex-col gap-1 text-sm">
                  {consequences.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}

          {requireTypedConfirmation && (
            <div className="flex flex-col gap-2">
              <p className="text-sm font-medium">
                Para confirmar, digite o nome:
              </p>
              <p className="text-sm font-semibold bg-muted p-2 rounded">
                {itemName}
              </p>
              <Input
                type="text"
                placeholder="Digite o nome aqui..."
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                disabled={isPending}
              />
            </div>
          )}
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
            onClick={onConfirm}
            disabled={!isConfirmed || isPending}
          >
            {isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
            Deletar Permanentemente
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
});
