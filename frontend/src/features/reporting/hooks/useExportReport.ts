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
    } catch (error) {
      const { message } = getApiErrorInfo(
        error,
        "Não foi possível exportar o relatório. Tente novamente.",
      );
      toast.error(message);
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
