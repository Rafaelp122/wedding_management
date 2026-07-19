import { useNavigate } from "react-router-dom";
import { useDashboardData } from "@/features/dashboard/hooks/useDashboardData";
import { getApiErrorInfo } from "@/api/error-utils";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { DashboardPageView } from "./DashboardPageView";

export default function DashboardPage() {
  const navigate = useNavigate();
  const dashboardData = useDashboardData();

  const handleNavigateToWedding = (weddingUuid: string, tab?: string) => {
    const url = `/weddings/${weddingUuid}${tab ? `?tab=${tab}` : ""}`;
    navigate(url);
  };

  if (dashboardData.lookupError) {
    const { message } = getApiErrorInfo(
      dashboardData.lookupError,
      "Não foi possível carregar os dados do painel.",
    );
    return (
      <div className="max-w-7xl mx-auto py-8 px-4">
        <Alert variant="destructive">
          <AlertCircle className="size-4" />
          <AlertTitle>Erro</AlertTitle>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return <DashboardPageView {...dashboardData} onNavigateToWedding={handleNavigateToWedding} />;
}
