"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useMemo } from "react";
import { BarChart as BarChartIcon } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { parseDecimal } from "@/features/shared/utils/formatters";
import type { BudgetCategoryOut } from "@/api/generated/v1/models/budgetCategoryOut";

interface WeddingFinancesDistributionChartProps {
  categories: BudgetCategoryOut[];
}

export function WeddingFinancesDistributionChart({
  categories,
}: WeddingFinancesDistributionChartProps) {
  const chartData = useMemo(
    () =>
      categories.map((cat) => ({
        name: cat.name,
        estimado: parseDecimal(cat.allocated_budget),
        real: parseDecimal(cat.total_spent),
      })),
    [categories],
  );

  return (
    <Card className="border-none shadow-sm">
      <CardHeader>
        <CardTitle className="text-lg font-bold flex items-center gap-2">
          <BarChartIcon className="w-5 h-5 text-violet-500" />
          Distribuição por Categoria
        </CardTitle>
        <CardDescription>
          Comparativo entre valores estimados e gastos reais
        </CardDescription>
      </CardHeader>
      <CardContent className="h-87.5 pt-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 0, right: 0, left: -20, bottom: 0 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#f0f0f0"
            />
            <XAxis
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#888", fontSize: 12 }}
              dy={10}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#888", fontSize: 12 }}
            />
            <Tooltip
              cursor={{ fill: "#f8f8f8" }}
              contentStyle={{
                borderRadius: "8px",
                border: "none",
                boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
              }}
            />
            <Legend iconType="circle" wrapperStyle={{ paddingTop: "20px" }} />
            <Bar
              dataKey="estimado"
              fill="#ddd6fe"
              radius={[4, 4, 0, 0]}
              name="Estimado"
            />
            <Bar
              dataKey="real"
              fill="#7c3aed"
              radius={[4, 4, 0, 0]}
              name="Realizado"
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
