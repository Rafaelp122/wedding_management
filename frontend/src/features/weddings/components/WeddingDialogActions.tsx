import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { DialogFooter } from "@/components/ui/dialog";

interface WeddingDialogActionsProps {
  isPending: boolean;
  submitLabel: string;
  onCancel: () => void;
}

export function WeddingDialogActions({
  isPending,
  submitLabel,
  onCancel,
}: WeddingDialogActionsProps) {
  return (
    <DialogFooter>
      <Button
        type="button"
        variant="outline"
        onClick={onCancel}
        disabled={isPending}
      >
        Cancelar
      </Button>
      <Button type="submit" disabled={isPending}>
        {isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
        {submitLabel}
      </Button>
    </DialogFooter>
  );
}
