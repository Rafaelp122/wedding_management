import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Heart, Calendar, DollarSign, Users, TrendingUp } from "lucide-react";

interface StatsCardsProps {
  totalWeddings: number;
  weddingsThisMonth?: number;
  totalRevenue?: string;
}

export function StatsCards({
  totalWeddings,
  weddingsThisMonth,
  totalRevenue,
}: StatsCardsProps) {
  const stats = [
    {
      title: "Casamentos Ativos",
      value: totalWeddings,
      icon: Heart,
      trend: "+20%",
      trendColor: "text-green-600 bg-green-50",
      color: "text-primary bg-primary/10",
    },
    {
      title: "Eventos este Mês",
      value: weddingsThisMonth ?? "0",
      icon: Calendar,
      color: "text-blue-600 bg-blue-50",
    },
    {
      title: "Convidados Gerenciados",
      value: "2.450", // Mock por enquanto
      icon: Users,
      color: "text-orange-600 bg-orange-50",
    },
    {
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
      {stats.map((stat, i) => (
        <Card key={i} className="shadow-sm border-zinc-200 dark:border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-4">
            <div className={`p-2 rounded-lg ${stat.color}`}>
              <stat.icon className="size-5" />
            </div>
            {stat.trend && (
              <span className={`flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full tabular-nums ${stat.trendColor}`}>
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
