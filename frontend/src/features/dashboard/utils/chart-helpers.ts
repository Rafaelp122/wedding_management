import type { WeddingByMonthOut } from "@/api/generated/v1/models/weddingByMonthOut";
import type { CashFlowMonthOut } from "@/api/generated/v1/models/cashFlowMonthOut";
import type { TaskProgressWeddingOut } from "@/api/generated/v1/models/taskProgressWeddingOut";

const MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"] as const;

export interface MonthlyWeddingData {
  name: string;
  casamentos: number;
}

export interface CashFlowData {
  name: string;
  pago: number;
  pendente: number;
}

export interface TaskProgressData {
  name: string;
  concluido: number;
}

/**
 * Transforma dados de casamentos agrupados por mês para o formato consumido pelo gráfico.
 *
 * @param byMonthData Lista opcional contendo a quantidade de casamentos por mês.
 * @returns Um objeto contendo a lista formatada de 12 meses e um booleano indicando se há dados reais.
 */
export function getMonthlyWeddingsData(
  byMonthData: WeddingByMonthOut[] | undefined,
): { monthlyData: MonthlyWeddingData[]; hasData: boolean } {
  const counts = Array.from({ length: 12 }, () => 0);
  const items = byMonthData ?? [];
  for (const item of items) {
    if (item.month >= 1 && item.month <= 12) {
      counts[item.month - 1] = item.count;
    }
  }
  const monthlyData = MONTHS.map((name, index) => ({
    name,
    casamentos: counts[index],
  }));
  return {
    monthlyData,
    hasData: monthlyData.some((d) => d.casamentos > 0),
  };
}

/**
 * Transforma a projeção mensal do backend no formato consumido pelo gráfico de fluxo de caixa.
 *
 * @param items Lista de projeções mensais calculadas pelo backend.
 * @returns Um objeto contendo a lista formatada e indicador se há dados de caixa.
 */
export function formatCashFlowData(
  items: CashFlowMonthOut[] | undefined,
): { cashFlowData: CashFlowData[]; hasCashFlowData: boolean } {
  const list = items ?? [];
  const cashFlowData = list.map((item) => ({
    name: MONTHS[item.month - 1] ?? `Mês ${item.month}`,
    pago: Number(item.paid) || 0,
    pendente: Number(item.pending) || 0,
  }));
  return {
    cashFlowData,
    hasCashFlowData: cashFlowData.some((d) => d.pago > 0 || d.pendente > 0),
  };
}

/**
 * Transforma o progresso de tarefas por casamento no formato consumido pelo gráfico de tarefas.
 *
 * @param items Lista de progresso de tarefas calculada pelo backend.
 * @returns Um objeto contendo a lista ordenada para o gráfico e indicador se há dados.
 */
export function formatTasksProgressData(
  items: TaskProgressWeddingOut[] | undefined,
): { tasksData: TaskProgressData[]; hasTasksData: boolean } {
  const list = items ?? [];
  const tasksData = list.map((item) => ({
    name: item.wedding_name || "Casamento",
    concluido: item.progress_pct,
  }));
  return {
    tasksData,
    hasTasksData: tasksData.length > 0,
  };
}
