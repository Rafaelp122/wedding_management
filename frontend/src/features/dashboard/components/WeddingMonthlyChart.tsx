"use client";

import { useMemo } from "react";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import type { ChartConfig } from "@/components/ui/chart";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";

interface WeddingMonthlyChartProps {
  weddings: WeddingOut[];
}

const MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"] as const;

const chartConfig = {
  casamentos: {
    label: "Casamentos",
    color: "hsl(var(--primary))",
  },
} satisfies ChartConfig;

export function WeddingMonthlyChart({ weddings }: WeddingMonthlyChartProps) {
  const currentYear = new Date().getFullYear();

  const { monthlyData, hasData } = useMemo(() => {
    const counts = new Array(12).fill(0);
    for (const w of weddings) {
      const date = new Date(w.date);
      if (date.getFullYear() === currentYear) {
        counts[date.getMonth()]++;
      }
    }
    const data = MONTHS.map((name, index) => ({
      name,
      casamentos: counts[index],
    }));
    return {
      monthlyData: data,
      hasData: counts.some((c) => c > 0),
    };
  }, [weddings, currentYear]);

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
