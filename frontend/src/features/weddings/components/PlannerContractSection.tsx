import { memo } from "react";
import type { PlannerContractOut } from "@/api/generated/v1/models/plannerContractOut";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatCurrencyBRCompact, formatDateBR } from "@/lib/formatters";
import { FileSignature, Pencil, Plus, Calendar, Layers, Hash } from "lucide-react";

interface PlannerContractSectionProps {
  contract?: PlannerContractOut | null;
  onEditContract: () => void;
}

const SERVICE_TIER_LABELS: Record<string, string> = {
  COMPLETA: "Assessoria Completa",
  PARCIAL: "Assessoria Parcial",
  FINAL: "Assessoria Final / Cerimonial",
};

const CONTRACT_STATUS_MAP: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  DRAFT: { label: "Rascunho", variant: "outline" },
  SIGNED: { label: "Assinado", variant: "default" },
  CANCELED: { label: "Cancelado", variant: "destructive" },
};

/**
 * Componente de apresentação (Dumb) para exibição do contrato de honorários da assessoria.
 * Totalmente síncrono e orientado a propriedades.
 */
export const PlannerContractSection = memo(function PlannerContractSection({
  contract,
  onEditContract,
}: PlannerContractSectionProps) {
  if (!contract) {
    return (
      <Card className="border-dashed border-zinc-300 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/20">
        <CardContent className="flex flex-col sm:flex-row items-center justify-between p-6 gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-primary/10 text-primary rounded-xl shrink-0">
              <FileSignature className="h-6 w-6" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                Contrato da Assessoria
              </h4>
              <p className="text-xs text-muted-foreground mt-0.5">
                Nenhum contrato de honorários cadastrado para este casamento.
              </p>
            </div>
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onEditContract}
            className="shrink-0 gap-1.5"
          >
            <Plus className="h-4 w-4" />
            Definir Contrato
          </Button>
        </CardContent>
      </Card>
    );
  }

  const serviceTierLabel =
    SERVICE_TIER_LABELS[contract.service_tier] ?? contract.service_tier;

  const statusInfo = CONTRACT_STATUS_MAP[contract.status] ?? {
    label: contract.status,
    variant: "secondary" as const,
  };

  const formattedSignedDate = contract.signed_date
    ? formatDateBR(contract.signed_date, {
        day: "2-digit",
        month: "short",
        year: "numeric",
      })
    : "Não assinado";

  return (
    <Card className="bg-white dark:bg-[#18181B] border-zinc-200 dark:border-zinc-800 shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-3 border-b bg-muted/20">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-primary/10 text-primary rounded-lg">
            <FileSignature className="h-4 w-4" />
          </div>
          <div>
            <CardTitle className="text-base font-semibold text-zinc-900 dark:text-white">
              Contrato de Assessoria
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              Honorários e escopo de atendimento acordados
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={statusInfo.variant} className="text-xs">
            {statusInfo.label}
          </Badge>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onEditContract}
            className="h-8 gap-1 text-xs"
            title="Editar contrato de assessoria"
          >
            <Pencil className="h-3.5 w-3.5" />
            Editar
          </Button>
        </div>
      </CardHeader>
      <CardContent className="pt-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div>
          <span className="flex items-center gap-1.5 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            <Layers className="h-3 w-3" /> Escopo
          </span>
          <p className="mt-1 text-sm font-semibold text-zinc-900 dark:text-white">
            {serviceTierLabel}
          </p>
        </div>

        <div>
          <span className="flex items-center gap-1.5 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            Honorários
          </span>
          <p className="mt-1 font-mono text-sm font-bold text-zinc-900 dark:text-white">
            {formatCurrencyBRCompact(contract.effective_amount)}
          </p>
        </div>

        <div>
          <span className="flex items-center gap-1.5 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            <Hash className="h-3 w-3" /> Parcelas
          </span>
          <p className="mt-1 text-sm font-medium text-zinc-900 dark:text-white">
            {contract.installments_count}{" "}
            {contract.installments_count === 1 ? "parcela" : "parcelas"}
          </p>
        </div>

        <div>
          <span className="flex items-center gap-1.5 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            <Calendar className="h-3 w-3" /> Assinatura
          </span>
          <p className="mt-1 text-sm font-medium text-zinc-900 dark:text-white">
            {formattedSignedDate}
          </p>
        </div>
      </CardContent>
    </Card>
  );
});
