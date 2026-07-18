import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import { useDashboardOperations } from "../hooks/useDashboardOperations";
import { DashboardOperationsView } from "./DashboardOperationsView";

interface DashboardOperationsProps {
  weddings: WeddingOut[];
}

export function DashboardOperations({ weddings }: DashboardOperationsProps) {
  const operations = useDashboardOperations({ weddings });

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
    />
  );
}
