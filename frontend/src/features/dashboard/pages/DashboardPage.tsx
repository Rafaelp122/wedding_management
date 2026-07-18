import { useState } from "react";
import { useWeddingsList, useWeddingsLookup, useWeddingsRead } from "@/api/generated/v1/endpoints/weddings/weddings";
import { useDashboardSummary, useDashboardWedding } from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { getApiErrorInfo } from "@/api/error-utils";
import { useAuthStore } from "@/stores/authStore";
import { getWeddingStatusInfo } from "@/features/weddings/utils/wedding-status";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { DashboardPageView } from "./DashboardPageView";

export default function DashboardPage() {
  const now = new Date();
  const [selectedYear, setSelectedYear] = useState(now.getFullYear());
  const [selectedWeddingUuid, setSelectedWeddingUuid] = useState<string>("all");
  const firstName = useAuthStore((state) => state.user?.first_name);

  // Hook enxuto para popular o combobox — apenas uuid, bride_name e groom_name
  const { data: lookupData, isLoading, error } = useWeddingsLookup();

  const isWeddingSelected = selectedWeddingUuid !== "all";

  // Lista completa apenas para o componente de operações (aba de casamentos)
  const { data: weddingsListData } = useWeddingsList(
    { limit: 200 },
    { query: { enabled: !isWeddingSelected } },
  );
  const { data: summaryData } = useDashboardSummary({
    query: { enabled: selectedWeddingUuid === "all" },
  });

  const { data: weddingDashboardData, isLoading: isLoadingWeddingDashboard } =
    useDashboardWedding(selectedWeddingUuid, {
      query: { enabled: isWeddingSelected },
    });

  // Dados completos do casamento selecionado (status, data, local) para o cabeçalho
  const { data: selectedWeddingData } = useWeddingsRead(selectedWeddingUuid, {
    query: { enabled: isWeddingSelected },
  });

  if (error) {
    const { message } = getApiErrorInfo(
      error,
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

  const weddingsArray = lookupData?.data ?? [];
  const fullWeddingsArray = weddingsListData?.data?.items ?? [];
  const summary = summaryData?.data;
  const weddingDashboard = weddingDashboardData?.data;

  const selectedWedding = isWeddingSelected
    ? (weddingsArray.find((w) => w.uuid === selectedWeddingUuid) ?? null)
    : null;
  const selectedWeddingFull = selectedWeddingData?.data ?? null;

  const greetingHour = now.getHours();
  const greeting =
    greetingHour < 12
      ? "Bom dia"
      : greetingHour < 18
        ? "Boa tarde"
        : "Boa noite";

  const formattedDate = now.toLocaleDateString("pt-BR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const weddingStatusInfo = selectedWeddingFull
    ? getWeddingStatusInfo(selectedWeddingFull.status)
    : null;

  const weddingDate = selectedWeddingFull
    ? new Date(selectedWeddingFull.date).toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
        timeZone: "UTC",
      })
    : null;

  return (
    <DashboardPageView
      greeting={greeting}
      formattedDate={formattedDate}
      firstName={firstName}
      selectedYear={selectedYear}
      setSelectedYear={setSelectedYear}
      selectedWeddingUuid={selectedWeddingUuid}
      setSelectedWeddingUuid={setSelectedWeddingUuid}
      isLoadingLookup={isLoading}
      weddingsArray={weddingsArray}
      isWeddingSelected={isWeddingSelected}
      selectedWeddingFull={selectedWeddingFull}
      selectedWedding={selectedWedding}
      weddingStatusInfo={weddingStatusInfo}
      weddingDate={weddingDate}
      isLoadingWeddingDashboard={isLoadingWeddingDashboard}
      weddingDashboard={weddingDashboard}
      summary={summary}
      fullWeddingsArray={fullWeddingsArray}
    />
  );
}
