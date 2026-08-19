import { FileDown, FileSpreadsheet, FileText, Loader2, Clock, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
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
  const { exportSync, exportAsync, isLoading } = useExportReport();

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
          disabled={isLoading}
          data-testid="export-report-dropdown-trigger"
        >
          {isLoading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <FileDown className="mr-2 h-4 w-4" />
          )}
          <span>Exportar Relatório</span>
          <ChevronDown className="ml-1.5 h-3.5 w-3.5 opacity-70" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">
          Download Imediato
        </DropdownMenuLabel>
        <DropdownMenuItem
          onSelect={() => exportSync(weddingUuid, "pdf", filenamePrefix)}
          onClick={() => exportSync(weddingUuid, "pdf", filenamePrefix)}
          className="cursor-pointer"
          data-testid="export-pdf-sync"
        >
          <FileText className="mr-2 h-4 w-4 text-rose-500" />
          <span>Relatório PDF (.pdf)</span>
        </DropdownMenuItem>
        <DropdownMenuItem
          onSelect={() => exportSync(weddingUuid, "excel", filenamePrefix)}
          onClick={() => exportSync(weddingUuid, "excel", filenamePrefix)}
          className="cursor-pointer"
          data-testid="export-excel-sync"
        >
          <FileSpreadsheet className="mr-2 h-4 w-4 text-emerald-600" />
          <span>Planilha Excel (.xlsx)</span>
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuLabel className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">
          Segundo Plano (Worker)
        </DropdownMenuLabel>
        <DropdownMenuItem
          onSelect={() => exportAsync(weddingUuid, "pdf")}
          onClick={() => exportAsync(weddingUuid, "pdf")}
          className="cursor-pointer"
          data-testid="export-pdf-async"
        >
          <Clock className="mr-2 h-4 w-4 text-muted-foreground" />
          <span>Processar PDF (Notificar)</span>
        </DropdownMenuItem>
        <DropdownMenuItem
          onSelect={() => exportAsync(weddingUuid, "excel")}
          onClick={() => exportAsync(weddingUuid, "excel")}
          className="cursor-pointer"
          data-testid="export-excel-async"
        >
          <Clock className="mr-2 h-4 w-4 text-muted-foreground" />
          <span>Processar Excel (Notificar)</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
