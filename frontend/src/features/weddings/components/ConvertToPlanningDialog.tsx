import { useQueryClient } from "@tanstack/react-query";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import {
  useConvertWeddingToPlanning,
  getWeddingsReadQueryKey,
  getWeddingsListQueryKey,
} from "@/api/generated/v1/endpoints/weddings/weddings";
import {
  getDashboardWeddingQueryKey,
  getDashboardSummaryQueryKey,
} from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { getSchedulerEventsListQueryKey } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { formatCurrencyBRCompact, formatDateBR } from "@/lib/formatters";
import { AlertCircle, CheckCircle2, Loader2, Sparkles } from "lucide-react";

interface ConvertToPlanningDialogProps {
  wedding: WeddingOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
  onOpenContractDialog?: () => void;
}

const SERVICE_TIER_LABELS: Record<string, string> = {
  COMPLETA: "Assessoria Completa",
  PARCIAL: "Assessoria Parcial",
  FINAL: "Assessoria Final / Cerimonial",
};

/**
 * Componente Smart para confirmação da conversão de PROPOSTA para PLANEJAMENTO.
 */
export function ConvertToPlanningDialog({
  wedding,
  open,
  onOpenChange,
  onSuccess,
  onOpenContractDialog,
}: ConvertToPlanningDialogProps) {
  const queryClient = useQueryClient();
  const { mutate, isPending } = useConvertWeddingToPlanning();

  const hasContract = Boolean(wedding.planner_contract);
  const contract = wedding.planner_contract;

  const handleConvert = () => {
    if (!hasContract) return;

    mutate(
      { uuid: wedding.uuid, data: null },
      createMutationCallbacks({
        successMsg: "Casamento convertido para planejamento com sucesso!",
        fallbackErrorMsg: "Erro ao converter casamento para planejamento.",
        onSuccess: () => {
          queryClient.invalidateQueries({
            queryKey: getWeddingsReadQueryKey(wedding.uuid),
          });
          queryClient.invalidateQueries({
            queryKey: getWeddingsListQueryKey(),
          });
          queryClient.invalidateQueries({
            queryKey: getDashboardWeddingQueryKey(wedding.uuid),
          });
          queryClient.invalidateQueries({
            queryKey: getSchedulerEventsListQueryKey(),
          });
          queryClient.invalidateQueries({
            queryKey: getDashboardSummaryQueryKey(),
          });
          onOpenChange(false);
          onSuccess?.();
        },
      }),
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[540px]">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary/10 text-primary rounded-lg">
              <Sparkles className="h-5 w-5" />
            </div>
            <DialogTitle>Efetivar Casamento</DialogTitle>
          </div>
          <DialogDescription>
            Converta esta proposta em um casamento em planejamento ativo.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {!hasContract ? (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Contrato da assessoria obrigatório</AlertTitle>
              <AlertDescription className="mt-1">
                Para efetivar a contratação e iniciar o planejamento, é
                necessário cadastrar os honorários e o contrato da assessoria.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="rounded-lg border bg-muted/30 p-4 space-y-3">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Resumo da Contratação
              </h4>
              <div className="grid grid-cols-2 gap-2.5 text-sm">
                <div>
                  <span className="text-xs text-muted-foreground">Noivos:</span>
                  <p className="font-semibold text-zinc-900 dark:text-white">
                    {wedding.groom_name} & {wedding.bride_name}
                  </p>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground">Data Prevista:</span>
                  <p className="font-semibold text-zinc-900 dark:text-white">
                    {formatDateBR(wedding.date)}
                  </p>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground">Escopo de Assessoria:</span>
                  <p className="font-medium text-zinc-900 dark:text-white">
                    {contract ? (SERVICE_TIER_LABELS[contract.service_tier] ?? contract.service_tier) : "—"}
                  </p>
                </div>
                <div>
                  <span className="text-xs text-muted-foreground">Honorários da Assessoria:</span>
                  <p className="font-mono font-bold text-zinc-900 dark:text-white">
                    {contract ? `${formatCurrencyBRCompact(contract.effective_amount)} (${contract.installments_count}x)` : "—"}
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="text-xs text-muted-foreground bg-muted/40 p-3 rounded-md flex items-start gap-2">
            <CheckCircle2 className="h-4 w-4 text-primary shrink-0 mt-0.5" />
            <p>
              Ao efetivar, as despesas de honorários serão geradas
              automaticamente no financeiro e os módulos de tarefas e
              cronograma serão habilitados.
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isPending}
          >
            Cancelar
          </Button>

          {!hasContract && onOpenContractDialog ? (
            <Button
              type="button"
              onClick={() => {
                onOpenChange(false);
                onOpenContractDialog();
              }}
            >
              Cadastrar Contrato Primeiro
            </Button>
          ) : (
            <Button
              type="button"
              onClick={handleConvert}
              disabled={!hasContract || isPending}
            >
              {isPending && <Loader2 className="mr-2 size-4 animate-spin" />}
              Efetivar Casamento
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
