import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Heart, Calendar, DollarSign, Users } from "lucide-react";

interface StatsCardsProps {
  totalWeddings: number;
  weddingsThisMonth?: number;
  pendingTasks?: number;
  totalRevenue?: string;
}

export function StatsCards({
  totalWeddings,
  weddingsThisMonth,
  pendingTasks,
  totalRevenue,
}: StatsCardsProps) {
  const stats = [
    {
      title: "Total de Casamentos",
      value: totalWeddings,
      icon: Heart,
      color: "text-primary",
    },
    {
      title: "Este Mês",
      value: weddingsThisMonth ?? "—",
      icon: Calendar,
      color: "text-info",
    },
    {
      title: "Tarefas Pendentes",
      value: pendingTasks ?? "—",
      icon: Users,
      color: "text-warning",
    },
    {
      title: "Orçamento Sob Gestão",
      value: totalRevenue ?? "—",
      icon: DollarSign,
      color: "text-success",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, i) => (
        <Card key={i}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
            <stat.icon className={`h-4 w-4 ${stat.color}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stat.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
