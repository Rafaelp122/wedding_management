import { useState } from "react";
import { toast } from "sonner";
import { reportsWeddingExport, useReportsWeddingExportAsync } from "@/api/generated/v1/endpoints/reports/reports";
import { getApiErrorInfo } from "@/api/error-utils";

export type ReportFormat = "pdf" | "excel";

interface UseExportReportOptions {
  onSuccess?: () => void;
}

export function useExportReport(options?: UseExportReportOptions) {
  const [isExportingSync, setIsExportingSync] = useState(false);
  const asyncMutation = useReportsWeddingExportAsync();

  const exportSync = async (
    weddingUuid: string,
    format: ReportFormat = "pdf",
    filenamePrefix = "relatorio-casamento",
  ) => {
    setIsExportingSync(true);
    try {
      const response = await reportsWeddingExport(
        weddingUuid,
        { format },
        { responseType: "blob" },
      );

      const mimeType =
        format === "excel"
          ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          : "application/pdf";
      const extension = format === "excel" ? "xlsx" : "pdf";
      const blob = new Blob([response.data as unknown as BlobPart], { type: mimeType });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${filenamePrefix}-${weddingUuid}.${extension}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      const formatLabel = format === "excel" ? "Excel" : "PDF";
      toast.success(`Relatório em ${formatLabel} exportado com sucesso!`);
      options?.onSuccess?.();
    } catch (error) {
      const { message } = getApiErrorInfo(
        error,
        "Não foi possível exportar o relatório. Tente novamente.",
      );
      toast.error(message);
    } finally {
      setIsExportingSync(false);
    }
  };

  const exportAsync = async (weddingUuid: string, format: ReportFormat = "pdf") => {
    try {
      const response = await asyncMutation.mutateAsync({
        uuid: weddingUuid,
        params: { format },
      });

      const formatLabel = format === "excel" ? "Excel" : "PDF";
      toast.info(
        response.data.detail ||
          `Geração do relatório (${formatLabel}) iniciada em segundo plano. Você será notificado quando estiver pronto.`,
      );
      options?.onSuccess?.();
    } catch (error) {
      const { message } = getApiErrorInfo(
        error,
        "Não foi possível iniciar a geração em segundo plano.",
      );
      toast.error(message);
    }
  };

  return {
    exportSync,
    exportAsync,
    isExportingSync,
    isExportingAsync: asyncMutation.isPending,
    isLoading: isExportingSync || asyncMutation.isPending,
  };
}
