import { FileDown, FileSpreadsheet, FileText, Loader2, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useExportReport } from "../hooks/useExportReport";

interface ExportReportDropdownProps {
  weddingUuid: string;
  weddingName?: string;
  variant?: "default" | "outline" | "secondary" | "ghost";
  size?: "default" | "sm" | "lg" | "icon";
  className?: string;
}

export function ExportReportDropdown({
  weddingUuid,
  weddingName,
  variant = "outline",
  size = "sm",
  className,
}: ExportReportDropdownProps) {
  const { exportReport, isExporting, exportingFormat } = useExportReport();

  const filenamePrefix = weddingName
    ? `relatorio-${weddingName.toLowerCase().replace(/[^a-z0-9]/g, "-")}`
    : "relatorio-casamento";

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant={variant}
          size={size}
          className={className}
          disabled={isExporting}
          data-testid="export-report-dropdown-trigger"
        >
          {isExporting ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <FileDown className="mr-2 h-4 w-4" />
          )}
          <span>{isExporting ? `Exportando ${exportingFormat?.toUpperCase()}...` : "Exportar"}</span>
          <ChevronDown className="ml-1.5 h-3.5 w-3.5 opacity-70" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-52">
        <DropdownMenuItem
          onSelect={() => exportReport(weddingUuid, "pdf", filenamePrefix)}
          onClick={() => exportReport(weddingUuid, "pdf", filenamePrefix)}
          className="cursor-pointer"
          data-testid="export-pdf"
        >
          <FileText className="mr-2 h-4 w-4 text-purple-600" />
          <span>Relatório (PDF)</span>
        </DropdownMenuItem>
        <DropdownMenuItem
          onSelect={() => exportReport(weddingUuid, "excel", filenamePrefix)}
          onClick={() => exportReport(weddingUuid, "excel", filenamePrefix)}
          className="cursor-pointer"
          data-testid="export-excel"
        >
          <FileSpreadsheet className="mr-2 h-4 w-4 text-emerald-600" />
          <span>Planilha (Excel)</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
