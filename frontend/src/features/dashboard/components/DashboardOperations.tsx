import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import { useNavigate } from "react-router-dom";
import { useDashboardOperations } from "../hooks/useDashboardOperations";
import { DashboardOperationsView } from "./DashboardOperationsView";

interface DashboardOperationsProps {
  weddings: WeddingOut[];
}

export function DashboardOperations({ weddings }: DashboardOperationsProps) {
  const operations = useDashboardOperations({ weddings });
  const navigate = useNavigate();

  const handleNavigateToWedding = (weddingUuid: string, tab?: string) => {
    const url = `/weddings/${weddingUuid}${tab ? `?tab=${tab}` : ""}`;
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
      weddingMap={operations.weddingMap}
      handleTaskToggle={operations.handleTaskToggle}
      todayStr={operations.todayStr}
      onNavigateToWedding={handleNavigateToWedding}
    />
  );
}
