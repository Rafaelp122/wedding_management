import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Heart, Calendar, DollarSign, Users, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatsCardsProps {
  totalWeddings: number;
  weddingsThisMonth?: number;
  totalRevenue?: string;
  activeFilter?: string | null;
  onFilterChange?: (filter: string | null) => void;
}

export function StatsCards({
  totalWeddings,
  weddingsThisMonth,
  totalRevenue,
  activeFilter,
  onFilterChange,
}: StatsCardsProps) {
  const stats = [
    {
      id: "all",
      title: "Casamentos Ativos",
      value: totalWeddings,
      icon: Heart,
      trend: "+20%",
      trendColor: "text-green-600 bg-green-50",
      color: "text-primary bg-primary/10",
    },
    {
      id: "month",
      title: "Eventos este Mês",
      value: weddingsThisMonth ?? "0",
      icon: Calendar,
      color: "text-blue-600 bg-blue-50",
    },
    {
      id: "guests",
      title: "Convidados Gerenciados",
      value: "2.450", // Mock por enquanto
      icon: Users,
      color: "text-orange-600 bg-orange-50",
    },
    {
      id: "budget",
      title: "Orçamento Sob Gestão",
      value: totalRevenue ?? "R$ 0",
      icon: DollarSign,
      trend: "+15%",
      trendColor: "text-green-600 bg-green-50",
      color: "text-green-600 bg-green-50",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card
          key={stat.id}
          className={cn(
            "shadow-sm border-zinc-200 dark:border-zinc-800 cursor-pointer transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] hover:shadow-md",
            activeFilter === stat.id && "ring-2 ring-primary bg-primary/5"
          )}
          onClick={() => onFilterChange?.(activeFilter === stat.id ? null : stat.id)}
        >
          <CardHeader className="flex flex-row items-center justify-between pb-4">
            <div className={cn("p-2 rounded-lg transition-colors", stat.color)}>
              <stat.icon className="size-5" />
            </div>
            {stat.trend && (
              <span className={cn("flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full tabular-nums", stat.trendColor)}>
                <TrendingUp className="size-3" /> {stat.trend}
              </span>
            )}
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
