import { memo, useMemo, useState } from "react";
import { useWeddingsByMonth } from "@/api/generated/v1/endpoints/weddings/weddings";
import {
  useDashboardChartCashFlow,
  useDashboardChartTaskProgress,
} from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { WeddingMonthlyChartView } from "./WeddingMonthlyChartView";
import {
  getMonthlyWeddingsData,
  formatCashFlowData,
  formatTasksProgressData,
} from "../utils/chart-helpers";

interface WeddingMonthlyChartProps {
  selectedYear: number;
  onYearChange: (year: number) => void;
}

export const WeddingMonthlyChart = memo(function WeddingMonthlyChart({
  selectedYear,
  onYearChange,
}: WeddingMonthlyChartProps) {
  const [activeTab, setActiveTab] = useState<string>("casamentos");

  // Chart 1: Weddings per Month
  const { data: byMonthData } = useWeddingsByMonth({ year: selectedYear });

  // Chart 2: Cash Flow
  const { data: cashFlowRes, isLoading: isLoadingInstallments } =
    useDashboardChartCashFlow(
      { year: selectedYear },
      { query: { enabled: activeTab === "financeiro" } },
    );

  // Chart 3: Tasks Progress
  const { data: taskProgressRes, isLoading: isLoadingTasks } =
    useDashboardChartTaskProgress(
      { year: selectedYear },
      { query: { enabled: activeTab === "tarefas" } },
    );

  // Compute monthly weddings data
  const { monthlyData, hasData } = useMemo(() => {
    return getMonthlyWeddingsData(byMonthData?.data);
  }, [byMonthData]);

  // Compute cash flow data
  const { cashFlowData, hasCashFlowData } = useMemo(() => {
    return formatCashFlowData(cashFlowRes?.data);
  }, [cashFlowRes]);

  // Compute tasks progress data
  const { tasksData, hasTasksData } = useMemo(() => {
    return formatTasksProgressData(taskProgressRes?.data);
  }, [taskProgressRes]);

  return (
    <WeddingMonthlyChartView
      selectedYear={selectedYear}
      onYearChange={onYearChange}
      activeTab={activeTab}
      onTabChange={setActiveTab}
      isLoadingInstallments={isLoadingInstallments}
      isLoadingTasks={isLoadingTasks}
      monthlyData={monthlyData}
      hasData={hasData}
      cashFlowData={cashFlowData}
      hasCashFlowData={hasCashFlowData}
      tasksData={tasksData}
      hasTasksData={hasTasksData}
    />
  );
});
