import { AlertTriangle } from "lucide-react";
import { useSchedulerTimelineCompressionGet } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface CompressedTimelineAlertProps {
  weddingUuid: string;
}

/**
 * Alerta operacional exibido quando a data do casamento está a menos de 90 dias (RF-18).
 * Indica que o checklist e prazos foram compactados automaticamente pelo backend.
 */
export function CompressedTimelineAlert({ weddingUuid }: CompressedTimelineAlertProps) {
  const { data: response, isLoading, isError } = useSchedulerTimelineCompressionGet(
    { wedding_id: weddingUuid },
    { query: { enabled: !!weddingUuid } },
  );

  // Compatibilidade com resposta envelopada por AxiosResponse (`response.data`)
  const compressionData = response?.data;

  if (isLoading || isError || !compressionData?.is_timeline_compressed) {
    return null;
  }

  const daysRemaining =
    compressionData.days_until_wedding !== null && compressionData.days_until_wedding !== undefined
      ? `${compressionData.days_until_wedding} dias restantes`
      : "< 90 dias";

  return (
    <Alert
      className="border-amber-500/50 bg-amber-50 text-amber-900 dark:border-amber-500 dark:bg-amber-950/30 dark:text-amber-200"
    >
      <AlertTriangle className="size-5 text-amber-600 dark:text-amber-400" />
      <AlertTitle className="font-semibold text-amber-900 dark:text-amber-200">
        Cronograma Comprimido ({daysRemaining})
      </AlertTitle>
      <AlertDescription className="text-amber-800 dark:text-amber-300">
        {compressionData.compressed_timeline_message ||
          "Atenção: Casamento com prazo inferior a 90 dias. As fases do checklist foram compactadas para garantir a execução das tarefas críticas a tempo."}
      </AlertDescription>
    </Alert>
  );
}
