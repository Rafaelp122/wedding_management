import { memo, useMemo, useState } from "react";
import { useFinancesInstallmentsList } from "@/api/generated/v1/endpoints/finances/finances";
import { useSchedulerTasksList } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { useWeddingsByMonth, useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { WeddingMonthlyChartView } from "./WeddingMonthlyChartView";
import { getMonthlyWeddingsData, getCashFlowData, getTasksProgressData } from "../utils/chart-helpers";

interface WeddingMonthlyChartProps {
  selectedYear: number;
  onYearChange: (year: number) => void;
}

export const WeddingMonthlyChart = memo(function WeddingMonthlyChart({
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
  const { data: byMonthData } = useWeddingsByMonth(
    { year: selectedYear },
  );

  const { data: weddingsData } = useWeddingsList({ limit: 200 });

  // Compute monthly weddings data
  const { monthlyData, hasData } = useMemo(() => {
    return getMonthlyWeddingsData(byMonthData?.data);
  }, [byMonthData]);

  // Compute cash flow data
  const { cashFlowData, hasCashFlowData } = useMemo(() => {
    return getCashFlowData(installmentsRes?.data?.items, selectedYear);
  }, [installmentsRes, selectedYear]);

  // Compute tasks progress data
  const { tasksData, hasTasksData } = useMemo(() => {
    return getTasksProgressData(weddingsData?.data?.items, tasksRes?.data?.items, selectedYear);
  }, [weddingsData, tasksRes, selectedYear]);

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
