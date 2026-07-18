import { memo } from "react";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import type { ChartConfig } from "@/components/ui/chart";
import { ChevronLeft, ChevronRight, BarChart2, DollarSign, CheckSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import type { MonthlyWeddingData, CashFlowData, TaskProgressData } from "../utils/chart-helpers";

interface WeddingMonthlyChartViewProps {
  selectedYear: number;
  onYearChange: (year: number) => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
  isLoadingInstallments: boolean;
  isLoadingTasks: boolean;
  monthlyData: MonthlyWeddingData[];
  hasData: boolean;
  cashFlowData: CashFlowData[];
  hasCashFlowData: boolean;
  tasksData: TaskProgressData[];
  hasTasksData: boolean;
}

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

export const WeddingMonthlyChartView = memo(function WeddingMonthlyChartView({
  selectedYear,
  onYearChange,
  activeTab,
  onTabChange,
  isLoadingInstallments,
  isLoadingTasks,
  monthlyData,
  hasData,
  cashFlowData,
  hasCashFlowData,
  tasksData,
  hasTasksData,
}: WeddingMonthlyChartViewProps) {
  return (
    <Card className="lg:col-span-2 shadow-soft border-zinc-200 dark:border-zinc-800 flex flex-col h-full">
      <Tabs value={activeTab} onValueChange={onTabChange} className="w-full flex flex-col h-full">
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
                <ChevronLeft aria-hidden="true" className="size-4" />
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
                <ChevronRight aria-hidden="true" className="size-4" />
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
                        // eslint-disable-next-line @typescript-eslint/no-explicit-any
                        formatter={(value: any, name: any) => {
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
                        // eslint-disable-next-line @typescript-eslint/no-explicit-any
                        formatter={(value: any) => `${value}% concluído`}
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
