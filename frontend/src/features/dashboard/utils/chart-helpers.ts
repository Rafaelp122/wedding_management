import type { WeddingByMonthOut } from "@/api/generated/v1/models/weddingByMonthOut";
import type { InstallmentOut } from "@/api/generated/v1/models/installmentOut";
import type { TaskOut } from "@/api/generated/v1/models/taskOut";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";

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
 * Transforma dados de casamentos por mês para o gráfico
 */
export function getMonthlyWeddingsData(
  byMonthData: WeddingByMonthOut[] | undefined
): { monthlyData: MonthlyWeddingData[]; hasData: boolean } {
  const counts = new Array(12).fill(0);
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
 * Transforma parcelas financeiras para o gráfico de fluxo de caixa
 */
export function getCashFlowData(
  installments: InstallmentOut[] | undefined,
  selectedYear: number
): { cashFlowData: CashFlowData[]; hasCashFlowData: boolean } {
  const paidSums = new Array(12).fill(0);
  const pendingSums = new Array(12).fill(0);

  const items = installments ?? [];
  for (const inst of items) {
    if (!inst.due_date) continue;
    const [year, month] = inst.due_date.split("-").map(Number);
    if (year === selectedYear && month >= 1 && month <= 12) {
      const amount = Number(inst.amount) || 0;
      if (inst.status === "PAID") {
        paidSums[month - 1] += amount;
      } else {
        pendingSums[month - 1] += amount;
      }
    }
  }

  const cashFlowData = MONTHS.map((name, index) => ({
    name,
    pago: paidSums[index],
    pendente: pendingSums[index],
  }));

  return {
    cashFlowData,
    hasCashFlowData: paidSums.some((s) => s > 0) || pendingSums.some((s) => s > 0),
  };
}

/**
 * Transforma tarefas e casamentos para o gráfico de progresso de tarefas (top 10)
 */
export function getTasksProgressData(
  weddings: WeddingOut[] | undefined,
  tasks: TaskOut[] | undefined,
  selectedYear: number
): { tasksData: TaskProgressData[]; hasTasksData: boolean } {
  const allWeddings = weddings ?? [];
  const allTasks = tasks ?? [];

  const yearWeddings = allWeddings.filter((w) => {
    if (!w.date) return false;
    const [year] = w.date.split("-").map(Number);
    return year === selectedYear;
  });

  if (yearWeddings.length === 0) return { tasksData: [], hasTasksData: false };

  const data = yearWeddings.map((w) => {
    const weddingTasks = allTasks.filter((t) => t.wedding === w.uuid);
    const total = weddingTasks.length;
    const completed = weddingTasks.filter((t) => t.is_completed).length;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

    // Pega o primeiro nome da noiva e do noivo
    const brideFirst = w.bride_name ? w.bride_name.split(" ")[0] : "";
    const groomFirst = w.groom_name ? w.groom_name.split(" ")[0] : "";
    return {
      name: brideFirst && groomFirst ? `${brideFirst} & ${groomFirst}` : brideFirst || groomFirst || "Casamento",
      concluido: percentage,
    };
  });

  const sortedData = data.sort((a, b) => b.concluido - a.concluido).slice(0, 10);

  return {
    tasksData: sortedData,
    hasTasksData: data.length > 0,
  };
}
