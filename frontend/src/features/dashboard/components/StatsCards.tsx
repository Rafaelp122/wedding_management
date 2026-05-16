import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Heart, DollarSign, Calendar, AlertTriangle } from "lucide-react";
import type { DashboardSummaryOut } from "@/api/generated/v1/models/dashboardSummaryOut";
import { formatCurrencyBRCompact } from "@/lib/formatters";

interface StatsCardsProps {
  summary?: DashboardSummaryOut;
}

export function StatsCards({ summary }: StatsCardsProps) {
  const stats = [
      {
        title: "Casamentos Ativos",
        value: summary?.active_weddings ?? 0,
        icon: Heart,
        color: "text-violet-600 bg-violet-50 dark:bg-violet-950/40",
      },
      {
        title: "Casamentos este Mês",
        value: summary?.weddings_this_month ?? 0,
        icon: Calendar,
        color: "text-blue-600 bg-blue-50 dark:bg-blue-950/40",
      },
      {
        title: "Parcelas a Vencer (7d)",
        value: formatCurrencyBRCompact(parseFloat(summary?.pending_installments_7d ?? "0"), 0),
        icon: DollarSign,
        color: "text-amber-600 bg-amber-50 dark:bg-amber-950/40",
      },
      {
        title: "Tarefas Atrasadas",
        value: summary?.urgent_tasks_count ?? 0,
        icon: AlertTriangle,
        color: "text-red-600 bg-red-50 dark:bg-red-950/40",
      },
    ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, i) => (
        <Card key={i} className="shadow-sm border-zinc-200 dark:border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-4">
            <div className={`p-2 rounded-lg ${stat.color}`}>
              <stat.icon className="size-5" />
            </div>
          </CardHeader>
          <CardContent className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
            <div className="text-3xl font-bold tracking-tight tabular-nums">{stat.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
