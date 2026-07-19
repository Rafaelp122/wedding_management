import { useMemo, useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import {
  useWeddingsLookup,
  useWeddingsList,
  useWeddingsRead,
} from "@/api/generated/v1/endpoints/weddings/weddings";
import {
  useDashboardSummary,
  useDashboardWedding,
} from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { getWeddingStatusInfo } from "@/features/weddings/utils/wedding-status";

/**
 * Hook que encapsula todas as queries de dados do dashboard.
 *
 * Centraliza fetching de lookup, listagem, summary, dashboard individual,
 * estado de seleção de casamento/ano, e valores derivados (saudação, data,
 * informações de status).
 *
 * @returns {DashboardData} Objeto com todos os dados e setters necessários.
 */
export function useDashboardData() {
  const firstName = useAuthStore((s) => s.user?.first_name ?? "");
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedWeddingUuid, setSelectedWeddingUuid] = useState<string | "all">("all");

  const isWeddingSelected = selectedWeddingUuid !== "all";

  // --- Queries ---
  const {
    data: lookupData,
    isLoading: isLoadingLookup,
    error: lookupError,
  } = useWeddingsLookup();

  const { data: summaryData } = useDashboardSummary({
    query: { enabled: !isWeddingSelected },
  });

  const { data: weddingsData } = useWeddingsList(
    { limit: 200 },
    { query: { enabled: !isWeddingSelected } },
  );

  const { data: weddingDashboardData, isLoading: isLoadingWeddingDashboard } =
    useDashboardWedding(selectedWeddingUuid, {
      query: { enabled: isWeddingSelected },
    });

  const { data: selectedWeddingData } = useWeddingsRead(selectedWeddingUuid, {
    query: { enabled: isWeddingSelected },
  });

  // --- Derived data ---
  const weddingsArray = lookupData?.data ?? [];
  const fullWeddingsArray = weddingsData?.data?.items ?? [];
  const summary = summaryData?.data;
  const weddingDashboard = weddingDashboardData?.data;

  const selectedWedding = isWeddingSelected
    ? (weddingsArray.find((w) => w.uuid === selectedWeddingUuid) ?? null)
    : null;
  const selectedWeddingFull = selectedWeddingData?.data ?? null;

  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return "Bom dia";
    if (hour < 18) return "Boa tarde";
    return "Boa noite";
  }, []);

  const formattedDate = useMemo(
    () =>
      new Date().toLocaleDateString("pt-BR", {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
      }),
    [],
  );

  const weddingStatusInfo = useMemo(
    () => (selectedWeddingFull ? getWeddingStatusInfo(selectedWeddingFull.status) : null),
    [selectedWeddingFull],
  );

  const weddingDate = useMemo(
    () =>
      selectedWeddingFull?.date
        ? new Date(selectedWeddingFull.date).toLocaleDateString("pt-BR", {
            day: "2-digit",
            month: "long",
            year: "numeric",
            timeZone: "UTC",
          })
        : null,
    [selectedWeddingFull],
  );

  return {
    greeting,
    formattedDate,
    firstName,
    selectedYear,
    setSelectedYear,
    selectedWeddingUuid,
    setSelectedWeddingUuid,
    isWeddingSelected,
    isLoadingLookup,
    lookupError,
    weddingsArray,
    selectedWedding,
    selectedWeddingFull,
    weddingStatusInfo,
    weddingDate,
    isLoadingWeddingDashboard,
    weddingDashboard,
    summary,
    fullWeddingsArray,
  } as const;
}
