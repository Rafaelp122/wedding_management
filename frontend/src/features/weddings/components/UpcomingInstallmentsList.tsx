import { memo } from "react";
import { Wallet } from "lucide-react";
import type { WeddingDashboardOut } from "@/api/generated/v1/models/weddingDashboardOut";
import { formatCurrencyBRCompact } from "@/lib/formatters";

type UpcomingInstallment = NonNullable<WeddingDashboardOut["upcoming_installments"]>[number];

interface UpcomingInstallmentsListProps {
  installments: UpcomingInstallment[];
}

export const UpcomingInstallmentsList = memo(function UpcomingInstallmentsList({
  installments,
}: UpcomingInstallmentsListProps) {
  if (installments.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-muted-foreground py-8">
        <Wallet className="w-8 h-8 text-muted/30 mb-3" />
        <p className="text-sm">Nenhum pagamento próximo.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {installments.map((inst) => (
        <div
          key={inst.uuid}
          className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors"
        >
          <div>
            <p className="text-sm font-medium">
              Parcela #{inst.installment_number}
            </p>
            <p className="text-xs text-muted-foreground mt-0.5">
              {new Intl.DateTimeFormat("pt-BR", {
                day: "2-digit",
                month: "short",
              }).format(new Date(inst.due_date))}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm font-semibold">
              {formatCurrencyBRCompact(Number(inst.amount), 0)}
            </p>
            <p className="text-xs text-orange-500 mt-0.5 font-medium">
              {inst.status === "OVERDUE" ? "Atrasado" : "Pendente"}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
});
