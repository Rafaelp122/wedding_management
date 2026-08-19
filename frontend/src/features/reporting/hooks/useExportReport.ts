import { useState } from "react";
import { toast } from "sonner";
import { reportsWeddingExport } from "@/api/generated/v1/endpoints/reports/reports";
import { getApiErrorInfo } from "@/api/error-utils";

export type ReportFormat = "pdf" | "excel";

interface UseExportReportOptions {
  onSuccess?: () => void;
}

export function useExportReport(options?: UseExportReportOptions) {
  const [exportingFormat, setExportingFormat] = useState<ReportFormat | null>(null);

  const exportReport = async (
    weddingUuid: string,
    format: ReportFormat = "pdf",
    filenamePrefix = "relatorio-casamento",
  ) => {
    setExportingFormat(format);
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
    } catch (error: unknown) {
      let errorMessage = "Não foi possível exportar o relatório. Tente novamente.";
      const axiosError = error as { response?: { data?: unknown } };

      if (axiosError?.response?.data instanceof Blob) {
        try {
          const text = await axiosError.response.data.text();
          const parsed = JSON.parse(text) as { message?: string; detail?: string };
          if (parsed.message) {
            errorMessage = parsed.message;
          } else if (parsed.detail) {
            errorMessage = parsed.detail;
          }
        } catch {
          const { message } = getApiErrorInfo(error, errorMessage);
          errorMessage = message;
        }
      } else {
        const { message } = getApiErrorInfo(error, errorMessage);
        errorMessage = message;
      }

      toast.error(errorMessage);
    } finally {
      setExportingFormat(null);
    }
  };

  return {
    exportReport,
    exportingFormat,
    isExporting: exportingFormat !== null,
  };
}
