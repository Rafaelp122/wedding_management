"use client";

import { Bar, BarChart, CartesianGrid, XAxis } from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import type { ChartConfig } from "@/components/ui/chart";
import type { BudgetCategoryOut } from "@/api/generated/v1/models";

interface WeddingBudgetChartProps {
  categories: BudgetCategoryOut[];
}

const chartConfig = {
  allocated_budget: {
    label: "Planejado (R$)",
    color: "hsl(var(--muted))",
  },
  total_spent: {
    label: "Realizado (R$)",
    color: "hsl(var(--primary))",
  },
} satisfies ChartConfig;

export function WeddingBudgetChart({ categories }: WeddingBudgetChartProps) {
  // Filtramos apenas categorias que tenham orçamento alocado ou gasto real
  const chartData = categories
    .filter(
      (cat) => Number(cat.allocated_budget) > 0 || Number(cat.total_spent) > 0
    )
    .map((cat) => ({
      name: cat.name,
      allocated_budget: Number(cat.allocated_budget),
      total_spent: Number(cat.total_spent || 0),
    }));

  if (chartData.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Planejado vs. Realizado</CardTitle>
        <CardDescription>
          Comparativo por categoria orçamentária
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart accessibilityLayer data={chartData}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="name"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 12)}
            />
            <ChartTooltip content={<ChartTooltipContent hideLabel />} />
            <ChartLegend content={<ChartLegendContent />} />
            <Bar
              dataKey="allocated_budget"
              fill="var(--color-allocated_budget)"
              radius={4}
            />
            <Bar
              dataKey="total_spent"
              fill="var(--color-total_spent)"
              radius={4}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
