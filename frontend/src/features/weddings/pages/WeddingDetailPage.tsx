import { useParams, Link } from "react-router-dom";
import { useMemo, useState } from "react";
import { useWeddingDetail } from "../hooks/useWeddingDetail";
import { useWeddingsOverviewRead } from "@/api/generated/v1/endpoints/weddings/weddings";
import { WeddingDetailTabs } from "@/features/weddings/components/WeddingDetailTabs";
import { EditWeddingDialog } from "@/features/weddings/components/EditWeddingDialog";
import { WeddingHeader } from "@/features/weddings/components/WeddingHeader";
import { calculateChecklistPercentage } from "@/features/weddings/utils/wedding-status";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

export default function WeddingDetailPage() {
  const { uuid } = useParams<{ uuid: string }>();
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  const { data: response, isLoading, error, invalidateWeddingQueries } = useWeddingDetail(uuid!);

  const wedding = response?.data;

  const overviewUuid = uuid!;
  const { data: overviewResponse, isLoading: isLoadingOverview } = useWeddingsOverviewRead(overviewUuid, {
    query: { enabled: !!overviewUuid },
  });
  const overview = overviewResponse?.data?.overview;
  const overviewWedding = overviewResponse?.data?.wedding;
  const weddingDate = overviewWedding?.date ?? wedding?.date;

  const displayDate = useMemo(() => {
    if (!weddingDate) return "";
    const dateObj = new Date(weddingDate + "T00:00:00");
    const day = dateObj.getDate();
    const monthNames = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
    const month = monthNames[dateObj.getMonth()];
    const year = dateObj.getFullYear();
    return `${day} ${month} ${year}`;
  }, [weddingDate]);

  const checklistPercentage = useMemo(() => {
    if (!overview) return 0;
    return calculateChecklistPercentage(overview.tasks_completed, overview.tasks_total);
  }, [overview]);

  if (!uuid) {
    return (
      <div className="flex flex-col gap-6 max-w-7xl mx-auto">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>URL inválida</AlertTitle>
          <AlertDescription>
            Nenhum UUID de casamento foi encontrado na URL.
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button asChild variant="outline">
            <Link to="/weddings">
              Voltar para lista
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6 max-w-7xl mx-auto">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-100 w-full" />
      </div>
    );
  }
  if (error) {
    return (
      <div className="flex flex-col gap-6 max-w-7xl mx-auto">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erro ao carregar casamento</AlertTitle>
          <AlertDescription>
            {error.message ||
              "Não foi possível carregar os dados do casamento."}
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button asChild variant="outline">
            <Link to="/weddings">
              Voltar para lista
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  if (!wedding) {
    return (
      <div className="flex flex-col gap-6 max-w-7xl mx-auto">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Casamento não encontrado</AlertTitle>
          <AlertDescription>
            O casamento solicitado não foi encontrado ou você não tem permissão
            para acessá-lo.
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button asChild variant="outline">
            <Link to="/weddings">
              Voltar para lista
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto animate-in fade-in duration-500">
      <WeddingHeader
        wedding={wedding}
        displayDate={displayDate}
        checklistPercentage={checklistPercentage}
        isLoadingOverview={isLoadingOverview}
        onEditClick={() => setEditDialogOpen(true)}
      />

      {/* Tabs de conteúdo */}
      <WeddingDetailTabs wedding={wedding} overview={overview} />

      <EditWeddingDialog
        wedding={wedding}
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        onSuccess={() => {
          invalidateWeddingQueries();
          setEditDialogOpen(false);
        }}
      />
    </div>
  );
}
