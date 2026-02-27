import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Heart, Calendar, DollarSign, Users } from "lucide-react";

interface StatsCardsProps {
  totalWeddings: number;
  weddingsThisMonth: number;
  pendingTasks: number;
  totalRevenue?: string;
}

export function StatsCards({
  totalWeddings,
  weddingsThisMonth,
  pendingTasks,
}: StatsCardsProps) {
  const stats = [
    {
      title: "Total de Casamentos",
      value: totalWeddings,
      icon: Heart,
      color: "text-pink-600",
    },
    {
      title: "Este Mês",
      value: weddingsThisMonth,
      icon: Calendar,
      color: "text-blue-600",
    },
    {
      title: "Tarefas Pendentes",
      value: pendingTasks,
      icon: Users,
      color: "text-orange-600",
    },
    {
      title: "Orçamento Sob Gestão",
      value: "R$ 45.000",
      icon: DollarSign,
      color: "text-green-600",
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
