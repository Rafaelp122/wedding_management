import { memo, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import type { ChartConfig } from "@/components/ui/chart";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import { ChevronLeft, ChevronRight, BarChart2, DollarSign, CheckSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useFinancesInstallmentsList } from "@/api/generated/v1/endpoints/finances/finances";
import { useSchedulerTasksList } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { Skeleton } from "@/components/ui/skeleton";

interface WeddingMonthlyChartProps {
  weddings: WeddingOut[];
  selectedYear: number;
  onYearChange: (year: number) => void;
}

const MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"] as const;

const weddingsConfig = {
  casamentos: {
    label: "Casamentos",
    color: "var(--color-primary)",
  },
} satisfies ChartConfig;

const cashFlowConfig = {
  pago: {
    label: "Pago",
    color: "var(--color-success)",
  },
  pendente: {
    label: "Pendente/Atrasado",
    color: "var(--color-warning)",
  },
} satisfies ChartConfig;

const tasksConfig = {
  concluido: {
    label: "Concluído (%)",
    color: "var(--color-primary)",
  },
} satisfies ChartConfig;

export const WeddingMonthlyChart = memo(function WeddingMonthlyChart({
  weddings,
  selectedYear,
  onYearChange,
}: WeddingMonthlyChartProps) {
  const [activeTab, setActiveTab] = useState<string>("casamentos");

  // API calls for Cash Flow and Tasks
  const { data: installmentsRes, isLoading: isLoadingInstallments } = useFinancesInstallmentsList(
    { limit: 200 },
    { query: { enabled: activeTab === "financeiro" } }
  );

  const { data: tasksRes, isLoading: isLoadingTasks } = useSchedulerTasksList(
    { limit: 200 },
    { query: { enabled: activeTab === "tarefas" } }
  );

  // Chart 1: Weddings per Month
  const { monthlyData, hasData } = useMemo(() => {
    const counts = new Array(12).fill(0);
    for (const w of weddings) {
      if (!w.date) continue;
      const [year, month] = w.date.split("-").map(Number);
      if (year === selectedYear) {
        counts[month - 1]++;
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
  }, [weddings, selectedYear]);

  // Chart 2: Cash Flow (previsto vs pago)
  const { cashFlowData, hasCashFlowData } = useMemo(() => {
    if (!installmentsRes?.data?.items) return { cashFlowData: [], hasCashFlowData: false };

    const paidSums = new Array(12).fill(0);
    const pendingSums = new Array(12).fill(0);

    for (const inst of installmentsRes.data.items) {
      if (!inst.due_date) continue;
      const [year, month] = inst.due_date.split("-").map(Number);
      if (year === selectedYear) {
        const amount = Number(inst.amount) || 0;
        if (inst.status === "PAID") {
          paidSums[month - 1] += amount;
        } else {
          pendingSums[month - 1] += amount;
        }
      }
    }

    const data = MONTHS.map((name, index) => ({
      name,
      pago: paidSums[index],
      pendente: pendingSums[index],
    }));

    return {
      cashFlowData: data,
      hasCashFlowData: paidSums.some((s) => s > 0) || pendingSums.some((s) => s > 0),
    };
  }, [installmentsRes, selectedYear]);

  // Chart 3: Tasks Progress per Wedding in selectedYear
  const { tasksData, hasTasksData } = useMemo(() => {
    const yearWeddings = weddings.filter((w) => {
      if (!w.date) return false;
      const [year] = w.date.split("-").map(Number);
      return year === selectedYear;
    });

    if (yearWeddings.length === 0) return { tasksData: [], hasTasksData: false };

    const data = yearWeddings.map((w) => {
      const weddingTasks = (tasksRes?.data?.items ?? []).filter((t) => t.wedding === w.uuid);
      const total = weddingTasks.length;
      const completed = weddingTasks.filter((t) => t.is_completed).length;
      const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

      return {
        name: `${w.bride_name.split(" ")[0]} & ${w.groom_name.split(" ")[0]}`,
        concluido: percentage,
      };
    });

    // Sort by completion percentage descending and display up to 10
    const sortedData = data.sort((a, b) => b.concluido - a.concluido).slice(0, 10);

    return {
      tasksData: sortedData,
      hasTasksData: data.length > 0,
    };
  }, [weddings, tasksRes, selectedYear]);

  return (
    <Card className="lg:col-span-2 shadow-soft border-zinc-200 dark:border-zinc-800 flex flex-col h-full">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full flex flex-col h-full">
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-100 dark:border-zinc-800/50 shrink-0">
          <div>
            <CardTitle className="text-base font-semibold text-zinc-900 dark:text-white">
              {activeTab === "casamentos" && "Casamentos por Mês"}
              {activeTab === "financeiro" && "Fluxo de Caixa Mensal"}
              {activeTab === "tarefas" && "Progresso de Cronograma"}
            </CardTitle>
            <CardDescription>
              {activeTab === "casamentos" && `Distribuição de casamentos ao longo de ${selectedYear}`}
              {activeTab === "financeiro" && `Receitas recebidas vs. previstas para ${selectedYear}`}
              {activeTab === "tarefas" && `Nível de conclusão do checklist dos casamentos de ${selectedYear}`}
            </CardDescription>
          </div>

          <div className="flex items-center gap-3 self-end sm:self-auto">
            <TabsList className="bg-zinc-100 dark:bg-zinc-800 h-9 p-0.5">
              <TabsTrigger value="casamentos" className="h-8 text-xs gap-1.5">
                <BarChart2 className="w-3.5 h-3.5" />
                Casamentos
              </TabsTrigger>
              <TabsTrigger value="financeiro" className="h-8 text-xs gap-1.5">
                <DollarSign className="w-3.5 h-3.5" />
                Financeiro
              </TabsTrigger>
              <TabsTrigger value="tarefas" className="h-8 text-xs gap-1.5">
                <CheckSquare className="w-3.5 h-3.5" />
                Tarefas
              </TabsTrigger>
            </TabsList>

            <div className="flex items-center gap-1 bg-background dark:bg-zinc-900 rounded-lg border shadow-sm border-zinc-200 dark:border-zinc-800 p-0.5 h-9">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-primary hover:bg-secondary focus-visible:ring-primary/50"
                onClick={() => onYearChange(selectedYear - 1)}
                aria-label="Ano anterior"
              >
                <ChevronLeft className="size-4" />
              </Button>
              <span className="text-sm font-semibold min-w-[50px] text-center font-mono">
                {selectedYear}
              </span>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-primary hover:bg-secondary focus-visible:ring-primary/50"
                onClick={() => onYearChange(selectedYear + 1)}
                aria-label="Próximo ano"
              >
                <ChevronRight className="size-4" />
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex-1 min-h-[300px] pt-6 relative">
          <TabsContent value="casamentos" className="m-0 h-full w-full">
            {hasData ? (
              <ChartContainer config={weddingsConfig} className="h-75 w-full">
                <BarChart data={monthlyData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "#71717A", fontSize: 12 }}
                    dy={10}
                  />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: "#71717A", fontSize: 12 }} />
                  <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                  <Bar
                    dataKey="casamentos"
                    fill="var(--color-primary)"
                    radius={[4, 4, 0, 0]}
                    maxBarSize={40}
                  />
                </BarChart>
              </ChartContainer>
            ) : (
              <div className="h-75 flex flex-col items-center justify-center text-muted-foreground border-2 border-dashed rounded-lg bg-zinc-50/50 dark:bg-zinc-900/10">
                <p className="text-sm italic">Nenhum casamento agendado para {selectedYear}.</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="financeiro" className="m-0 h-full w-full">
            {isLoadingInstallments ? (
              <div className="h-75 flex flex-col justify-end gap-3 pb-4">
                <div className="flex items-end gap-4 h-full px-4">
                  {[35, 65, 45, 80, 50, 75, 40, 60, 30, 85, 55, 70].map((height, i) => (
                    <Skeleton key={i} className="flex-1" style={{ height: `${height}%` }} />
                  ))}
                </div>
              </div>
            ) : hasCashFlowData ? (
              <ChartContainer config={cashFlowConfig} className="h-75 w-full">
                <BarChart data={cashFlowData} margin={{ top: 0, right: 0, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "#71717A", fontSize: 12 }}
                    dy={10}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "#71717A", fontSize: 10 }}
                    tickFormatter={(val) => `R$ ${val >= 1000 ? `${val / 1000}k` : val}`}
                  />
                  <ChartTooltip
                    content={
                      <ChartTooltipContent
                        formatter={(value, name) => {
                          const config = cashFlowConfig[name as keyof typeof cashFlowConfig];
                          const label = config ? config.label : name;
                          const formattedValue = new Intl.NumberFormat("pt-BR", {
                            style: "currency",
                            currency: "BRL",
                          }).format(Number(value));
                          return (
                            <div className="flex items-center gap-1.5">
                              <span className="font-medium">{label}:</span>
                              <span className="font-semibold">{formattedValue}</span>
                            </div>
                          );
                        }}
                      />
                    }
                  />
                  <Bar dataKey="pago" stackId="a" fill="var(--color-success)" radius={[0, 0, 0, 0]} maxBarSize={30} />
                  <Bar dataKey="pendente" stackId="a" fill="var(--color-warning)" radius={[4, 4, 0, 0]} maxBarSize={30} />
                </BarChart>
              </ChartContainer>
            ) : (
              <div className="h-75 flex flex-col items-center justify-center text-muted-foreground border-2 border-dashed rounded-lg bg-zinc-50/50 dark:bg-zinc-900/10">
                <p className="text-sm italic">Nenhum compromisso financeiro para {selectedYear}.</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="tarefas" className="m-0 h-full w-full">
            {isLoadingTasks ? (
              <div className="h-75 flex flex-col gap-4 justify-center">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <Skeleton className="h-4 w-24 shrink-0" />
                    <Skeleton className="h-4 flex-1 rounded" />
                  </div>
                ))}
              </div>
            ) : hasTasksData ? (
              <ChartContainer config={tasksConfig} className="h-75 w-full">
                <BarChart
                  data={tasksData}
                  layout="vertical"
                  margin={{ top: 0, right: 10, left: 10, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                  <XAxis type="number" domain={[0, 100]} tickFormatter={(val) => `${val}%`} />
                  <YAxis
                    dataKey="name"
                    type="category"
                    width={90}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "#71717A", fontSize: 11 }}
                  />
                  <ChartTooltip
                    content={
                      <ChartTooltipContent
                        formatter={(value) => `${value}% concluído`}
                        hideLabel
                      />
                    }
                  />
                  <Bar
                    dataKey="concluido"
                    fill="var(--color-primary)"
                    radius={[0, 4, 4, 0]}
                    maxBarSize={16}
                  />
                </BarChart>
              </ChartContainer>
            ) : (
              <div className="h-75 flex flex-col items-center justify-center text-muted-foreground border-2 border-dashed rounded-lg bg-zinc-50/50 dark:bg-zinc-900/10">
                <p className="text-sm italic">Nenhum casamento com tarefas em {selectedYear}.</p>
              </div>
            )}
          </TabsContent>
        </CardContent>
      </Tabs>
    </Card>
  );
});
