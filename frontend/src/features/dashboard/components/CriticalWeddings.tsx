import { Link } from "react-router-dom";
import { ArrowRight, AlertTriangle, Clock, DollarSign } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { CriticalWeddingOut } from "@/api/generated/v1/models/criticalWeddingOut";

interface CriticalWeddingsProps {
  weddings: CriticalWeddingOut[];
}

function daysBadge(days: number) {
  if (days <= 30)
    return { variant: "destructive" as const, label: `${days}d` };
  if (days <= 90)
    return { variant: "outline" as const, label: `${days}d` };
  return { variant: "secondary" as const, label: `${days}d` };
}

function reasonLine(w: CriticalWeddingOut): string | null {
  const parts: string[] = [];
  if (w.overdue_tasks > 0)
    parts.push(`${w.overdue_tasks} tarefa${w.overdue_tasks > 1 ? "s" : ""} atrasada${w.overdue_tasks > 1 ? "s" : ""}`);
  if (w.overdue_installments > 0)
    parts.push(`${w.overdue_installments} parcela${w.overdue_installments > 1 ? "s" : ""} vencida${w.overdue_installments > 1 ? "s" : ""}`);
  if (parts.length > 0) return parts.join(" • ");
  if (w.days_until <= 60 && w.incomplete_tasks > 0)
    return "Revisar planejamento";
  if (w.days_until <= 30)
    return "Evento próximo — revisar pendências";
  return null;
}

export function CriticalWeddings({ weddings }: CriticalWeddingsProps) {
  if (weddings.length === 0) return null;

  return (
    <Card className="border-red-200 dark:border-red-900/30 shadow-sm">
      <CardHeader className="pb-3 border-b bg-red-50/50 dark:bg-red-950/20">
        <div className="flex items-center gap-2">
          <AlertTriangle className="size-4 text-red-500" />
          <CardTitle className="text-base font-semibold text-red-800 dark:text-red-200">
            Casamentos que Precisam de Atenção
          </CardTitle>
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {weddings.map((w) => {
            const badge = daysBadge(w.days_until);
            const reason = reasonLine(w);
            return (
              <Link
                key={w.uuid}
                to={`/weddings/${w.uuid}`}
                className="block p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors group"
              >
                <div className="flex items-start justify-between mb-1">
                  <p className="text-sm font-semibold truncate pr-2">
                    {w.groom_name} & {w.bride_name}
                  </p>
                  <Badge variant={badge.variant} className="shrink-0 text-[10px] h-5">
                    {badge.label}
                  </Badge>
                </div>
                {reason && (
                  <p className="text-xs text-red-600 dark:text-red-400 font-medium mb-2">
                    {reason}
                  </p>
                )}
                <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                  {w.incomplete_tasks > 0 && (
                    <span className="flex items-center gap-1">
                      <Clock className="size-3" />
                      {w.incomplete_tasks} pendente{w.incomplete_tasks > 1 ? "s" : ""}
                    </span>
                  )}
                  {w.pending_installments > 0 && (
                    <span className="flex items-center gap-1">
                      <DollarSign className="size-3" />
                      {w.pending_installments} parcela{w.pending_installments > 1 ? "s" : ""}
                    </span>
                  )}
                </div>
                <div className="flex items-center justify-end mt-2">
                  <span className="text-xs text-primary group-hover:underline flex items-center gap-1">
                    Ver detalhes <ArrowRight className="size-3" />
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
