import { Users, AlertTriangle } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface GuestCountChangeNoticeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  previousGuestCount?: number | null;
  newGuestCount?: number | null;
  onConfirm?: () => void;
}

/**
 * Dialog informativo exibido quando o número previsto de convidados de um casamento é alterado (RF-14).
 * Alerta o assessor de que fornecedores sensíveis à contagem (buffet, papelaria, bar)
 * estão sendo avaliados e recomenda a revisão de aditivos contratuais.
 */
export function GuestCountChangeNoticeDialog({
  open,
  onOpenChange,
  previousGuestCount,
  newGuestCount,
  onConfirm,
}: GuestCountChangeNoticeDialogProps) {
  const handleClose = () => {
    onOpenChange(false);
    onConfirm?.();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 mb-1">
            <AlertTriangle className="size-5" />
            <span className="text-xs font-semibold uppercase tracking-wider">
              Aviso de Dimensionamento (RF-14)
            </span>
          </div>
          <DialogTitle className="text-lg">
            Alteração no Número de Convidados
          </DialogTitle>
          <DialogDescription className="text-sm">
            {previousGuestCount && newGuestCount ? (
              <>
                A estimativa de convidados foi atualizada de{" "}
                <strong>{previousGuestCount}</strong> para{" "}
                <strong>{newGuestCount}</strong> convidados.
              </>
            ) : (
              "A contagem estimada de convidados deste evento foi modificada."
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-3 py-2 text-sm text-muted-foreground">
          <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50/50 p-3 dark:border-amber-900/50 dark:bg-amber-950/20">
            <Users className="size-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <p className="text-xs text-amber-900 dark:text-amber-200 leading-relaxed">
              O sistema disparou em segundo plano a análise de impacto em
              fornecedores sensíveis à contagem (buffet, bar, papelaria e
              mobiliário).
            </p>
          </div>
          <p className="text-xs leading-relaxed">
            Recomendamos revisar a aba de <strong>Contratos</strong> caso seja
            necessário formalizar um <em>Aditivo Contratual</em> com valores
            proporcionais atualizados.
          </p>
        </div>

        <DialogFooter>
          <Button onClick={handleClose} className="w-full sm:w-auto">
            Entendido
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
