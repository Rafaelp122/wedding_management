import { type EventOut } from "@/api/generated/v1/models/eventOut";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Lock } from "lucide-react";

interface ReadOnlyEventDetailsProps {
  event: EventOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ReadOnlyEventDetails({
  event,
  open,
  onOpenChange,
}: ReadOnlyEventDetailsProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[560px]">
        <DialogHeader>
          <DialogTitle>Detalhes do Evento</DialogTitle>
          <DialogDescription>
            Evento de pagamento gerado automaticamente.
          </DialogDescription>
        </DialogHeader>

        <Alert>
          <Lock className="h-4 w-4" />
          <AlertTitle>Evento somente leitura</AlertTitle>
          <AlertDescription>
            Este evento de pagamento foi gerado automaticamente a partir de
            uma parcela. Para modificá-lo, ajuste a parcela correspondente
            no módulo financeiro.
          </AlertDescription>
        </Alert>

        <div className="space-y-3 text-sm">
          <div>
            <span className="font-medium">Título: </span>
            {event.title}
          </div>
          <div>
            <span className="font-medium">Tipo: </span>Pagamento
          </div>
          <div>
            <span className="font-medium">Início: </span>
            {new Date(event.start_time).toLocaleString("pt-BR")}
          </div>
          {event.end_time && (
            <div>
              <span className="font-medium">Fim: </span>
              {new Date(event.end_time).toLocaleString("pt-BR")}
            </div>
          )}
          {event.location && (
            <div>
              <span className="font-medium">Local: </span>
              {event.location}
            </div>
          )}
          {event.description && (
            <div>
              <span className="font-medium">Descrição: </span>
              {event.description}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button type="button" onClick={() => onOpenChange(false)}>
            Fechar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
