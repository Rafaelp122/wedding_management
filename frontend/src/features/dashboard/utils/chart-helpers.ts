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
 * Transforma dados de casamentos agrupados por mês para o formato consumido pelo gráfico.
 *
 * @param byMonthData Lista opcional contendo a quantidade de casamentos por mês.
 * @returns Um objeto contendo a lista formatada de 12 meses e um booleano indicando se há dados reais.
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
 * Transforma as parcelas financeiras no formato necessário para o gráfico de fluxo de caixa.
 *
 * Filtra as parcelas pelo ano selecionado e calcula o total acumulado das parcelas
 * pagas e pendentes para cada mês do ano, arredondando os valores acumulados finais
 * para 2 casas decimais conforme a regra de precisão monetária BR-VAL01.
 *
 * @param installments Lista opcional contendo todas as parcelas cadastradas.
 * @param selectedYear O ano para o qual o fluxo de caixa deve ser gerado.
 * @returns Um objeto contendo a lista de dados mensais formatados e um indicador se há dados de caixa.
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

  // Garante o arredondamento dos acumulados para 2 casas decimais (BR-VAL01)
  const cashFlowData = MONTHS.map((name, index) => ({
    name,
    pago: Math.round(paidSums[index] * 100) / 100,
    pendente: Math.round(pendingSums[index] * 100) / 100,
  }));

  return {
    cashFlowData,
    hasCashFlowData: paidSums.some((s) => s > 0) || pendingSums.some((s) => s > 0),
  };
}

/**
 * Transforma a lista de tarefas e casamentos no progresso geral de checklists (Top 10).
 *
 * Calcula a porcentagem de tarefas concluídas por casamento e ordena os 10 casamentos
 * de maior progresso no ano selecionado.
 *
 * @param weddings Lista opcional de casamentos cadastrados.
 * @param tasks Lista opcional de tarefas cadastradas.
 * @param selectedYear Ano de referência para filtragem.
 * @returns Um objeto contendo a lista dos 10 casamentos com melhor progresso e indicador se há tarefas.
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
