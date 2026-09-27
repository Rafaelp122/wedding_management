import { useNavigate } from "react-router-dom";
import { useDashboardOperations } from "../hooks/useDashboardOperations";
import { DashboardOperationsView } from "./DashboardOperationsView";

interface DashboardOperationsProps {
  weddings?: unknown;
}

export function DashboardOperations(_props?: DashboardOperationsProps) {
  const operations = useDashboardOperations();
  const navigate = useNavigate();

  const handleNavigateToWedding = (weddingUuid: string, tab?: string) => {
    const url = weddingUuid ? `/weddings/${weddingUuid}${tab ? `?tab=${tab}` : ""}` : "/weddings";
    navigate(url);
  };

  return (
    <DashboardOperationsView
      activeTab={operations.activeTab}
      onTabChange={operations.setActiveTab}
      isLoadingTasks={operations.isLoadingTasks}
      isLoadingContracts={operations.isLoadingContracts}
      isUpdatingTask={operations.isUpdatingTask}
      displayWeddings={operations.displayWeddings}
      urgentTasks={operations.urgentTasks}
      pendingContracts={operations.pendingContracts}
      handleTaskToggle={operations.handleTaskToggle}
      todayStr={operations.todayStr}
      onNavigateToWedding={handleNavigateToWedding}
    />
  );
}
