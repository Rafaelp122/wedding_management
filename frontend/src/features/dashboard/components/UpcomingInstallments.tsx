import { useState } from "react";
import { Link } from "react-router-dom";
import { Wallet, ArrowRight, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useFinancesInstallmentsList } from "@/api/generated/v1/endpoints/finances/finances";
import { formatCurrencyBR, formatDateBR } from "@/lib/formatters";

const PERIOD_OPTIONS = [7, 14, 30] as const;

export function UpcomingInstallments() {
  const [days, setDays] = useState<number>(7);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const cutoff = new Date(today);
  cutoff.setDate(cutoff.getDate() + days);

  const { data } = useFinancesInstallmentsList({ limit: 100 });

  const installments = (data?.data?.items ?? [])
    .filter((inst) => {
      if (inst.status !== "PENDING") return false;
      const dueDate = new Date(inst.due_date);
      dueDate.setHours(0, 0, 0, 0);
      return dueDate >= today && dueDate <= cutoff;
    })
    .sort(
      (a, b) =>
        new Date(a.due_date).getTime() - new Date(b.due_date).getTime(),
    );

  if (installments.length === 0) return null;

  return (
    <Card className="border-orange-200 dark:border-orange-900/30 shadow-sm">
      <CardHeader className="pb-3 border-b bg-orange-50/50 dark:bg-orange-950/20">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2 text-orange-800 dark:text-orange-200">
            <AlertCircle className="size-4" />
            Parcelas a Vencer
          </CardTitle>
          <div className="flex items-center gap-1">
            <div className="flex items-center gap-0.5 bg-background rounded-md border p-0.5 mr-2">
              {PERIOD_OPTIONS.map((d) => (
                <button
                  key={d}
                  onClick={() => setDays(d)}
                  className={`px-2 py-0.5 text-xs rounded-sm font-medium transition-colors ${
                    days === d
                      ? "bg-orange-500 text-white"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {d}d
                </button>
              ))}
            </div>
            <Badge
              variant="outline"
              className="text-xs border-orange-200 text-orange-700 dark:border-orange-800 dark:text-orange-300"
            >
              {installments.length} pendente{installments.length > 1 ? "s" : ""}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-4">
        <div className="space-y-3">
          {installments.map((inst) => (
            <div
              key={inst.uuid}
              className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full flex items-center justify-center bg-orange-100 text-orange-500 dark:bg-orange-950 dark:text-orange-400">
                  <Wallet className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-sm font-medium">
                    Parcela #{inst.installment_number}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Vencimento:{" "}
                    {formatDateBR(inst.due_date, { day: "2-digit", month: "short" })}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold tabular-nums">
                  {formatCurrencyBR(Number(inst.amount))}
                </p>
                {inst.wedding ? (
                  <Link
                    to={`/weddings/${inst.wedding}?tab=finances`}
                    className="text-xs text-primary hover:underline flex items-center gap-1 justify-end mt-0.5"
                  >
                    Ver finanças <ArrowRight className="size-3" />
                  </Link>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
