"use client";

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import type { ChartConfig } from "@/components/ui/chart";
import type { WeddingOut } from "@/api/generated/v1/models";

interface WeddingMonthlyChartProps {
  weddings: WeddingOut[];
}

const chartConfig = {
  casamentos: {
    label: "Casamentos",
    color: "hsl(var(--primary))",
  },
} satisfies ChartConfig;

export function WeddingMonthlyChart({ weddings }: WeddingMonthlyChartProps) {
  // Agrupar casamentos por mês para o ano atual
  const currentYear = new Date().getFullYear();
  const months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

  const monthlyData = months.map((month, index) => {
    const count = weddings.filter((w) => {
      const date = new Date(w.date);
      return date.getMonth() === index && date.getFullYear() === currentYear;
    }).length;

    return { name: month, casamentos: count };
  });

  const hasData = monthlyData.some(d => d.casamentos > 0);

  return (
    <Card className="lg:col-span-2">
      <CardHeader>
        <CardTitle className="text-base font-semibold">Eventos por Mês</CardTitle>
        <CardDescription>Distribuição de casamentos ao longo de {currentYear}</CardDescription>
      </CardHeader>
      <CardContent className="h-75 w-full pt-4">
        {hasData ? (
          <ChartContainer config={chartConfig} className="h-full w-full">
            <BarChart data={monthlyData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E4E4E7" />
              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#71717A', fontSize: 12 }}
                dy={10}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: '#71717A', fontSize: 12 }}
              />
              <ChartTooltip content={<ChartTooltipContent hideLabel />} />
              <Bar
                dataKey="casamentos"
                fill="hsl(var(--primary))"
                radius={[4, 4, 0, 0]}
                maxBarSize={40}
              />
            </BarChart>
          </ChartContainer>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-muted-foreground border-2 border-dashed rounded-lg bg-zinc-50/50">
            <p className="text-sm italic">Nenhum evento agendado para {currentYear}.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
