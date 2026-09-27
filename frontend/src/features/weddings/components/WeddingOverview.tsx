import {
  CalendarHeart,
  Wallet,
  CheckSquare,
  FileText,
  AlertCircle,
  Clock,
  ArrowRight,
} from "lucide-react";
import { useState, useMemo } from "react";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import type { WeddingDashboardOut } from "@/api/generated/v1/models/weddingDashboardOut";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getWeddingStatusInfo } from "@/features/weddings/utils/wedding-status";
import { formatDateBR } from "@/lib/formatters";
import { ExportReportDropdown } from "@/features/reporting/components/ExportReportDropdown";
import { UrgentTasksList } from "./UrgentTasksList";
import { UpcomingInstallmentsList } from "./UpcomingInstallmentsList";
import { PlannerContractSection } from "./PlannerContractSection";
import { PlannerContractDialog } from "./PlannerContractDialog";
import { WeddingParticipantsSection } from "./WeddingParticipantsSection";
import { AddParticipantDialog } from "./AddParticipantDialog";
import {
  useRemoveWeddingParticipant,
  getWeddingsReadQueryKey,
  getWeddingsListQueryKey,
} from "@/api/generated/v1/endpoints/weddings/weddings";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import type { WeddingParticipantOut } from "@/api/generated/v1/models/weddingParticipantOut";

interface WeddingOverviewProps {
  wedding: WeddingOut;
  overview?: WeddingDashboardOut | null;
  onNavigateToPlanning?: () => void;
  onNavigateToFinances?: () => void;
  onEditContract?: () => void;
}

export function WeddingOverview({
  wedding,
  overview,
  onNavigateToPlanning,
  onNavigateToFinances,
  onEditContract,
}: WeddingOverviewProps) {
  const [contractDialogOpen, setContractDialogOpen] = useState(false);
  const [participantDialogOpen, setParticipantDialogOpen] = useState(false);
  const queryClient = useQueryClient();
  const statusInfo = getWeddingStatusInfo(wedding.status);

  const removeParticipantMutation = useRemoveWeddingParticipant({
    mutation: {
      onSuccess: () => {
        toast.success("Participante desvinculado com sucesso.");
        queryClient.invalidateQueries({
          queryKey: getWeddingsReadQueryKey(wedding.uuid),
        });
        queryClient.invalidateQueries({
          queryKey: getWeddingsListQueryKey(),
        });
      },
      onError: () => {
        toast.error("Erro ao remover participante.");
      },
    },
  });

  const handleRemoveParticipant = (participant: WeddingParticipantOut) => {
    removeParticipantMutation.mutate({
      uuid: wedding.uuid,
      participantUuid: participant.uuid,
    });
  };

  const urgentTasks = overview?.urgent_tasks ?? [];
  const upcomingInstallments = overview?.upcoming_installments ?? [];

  const handleEditContract = () => {
    if (onEditContract) {
      onEditContract();
    } else {
      setContractDialogOpen(true);
    }
  };

  const formattedDate = useMemo(
    () => formatDateBR(wedding.date, { day: "2-digit", month: "long", year: "numeric" }),
    [wedding.date],
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            {wedding.groom_name} & {wedding.bride_name}
          </h2>
          <p className="text-muted-foreground mt-1">
            {formattedDate}{" "}
            • {wedding.location}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <ExportReportDropdown
            weddingUuid={wedding.uuid}
            weddingName={`${wedding.groom_name}-${wedding.bride_name}`}
          />
          <Badge variant={statusInfo.variant} className="w-fit text-sm py-1 px-3">
            {statusInfo.label}
          </Badge>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center gap-3 pb-2 space-y-0">
            <div className="p-2 bg-primary/10 text-primary rounded-lg">
              <CalendarHeart className="w-5 h-5" />
            </div>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Contagem Regressiva
            </CardTitle>
          </CardHeader>
          <CardContent className="mt-auto">
            <div className="text-3xl font-bold">{overview?.days_until_wedding ?? "—"}</div>
            <p className="text-xs text-muted-foreground mt-1">
              dias para o grande dia
            </p>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center gap-3 pb-2 space-y-0">
            <div className="p-2 bg-primary/10 text-primary rounded-lg">
              <Wallet className="w-5 h-5" />
            </div>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Saúde Financeira
            </CardTitle>
          </CardHeader>
          <CardContent className="mt-auto">
            <div className="flex items-end justify-between mb-2">
              <p className="text-2xl font-bold">{overview?.budget_percentage_used ?? 0}%</p>
              <p className="text-xs text-muted-foreground mb-1">utilizado</p>
            </div>
            <Progress value={overview?.budget_percentage_used ?? 0} className="h-2" />
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center gap-3 pb-2 space-y-0">
            <div className="p-2 bg-primary/10 text-primary rounded-lg">
              <CheckSquare className="w-5 h-5" />
            </div>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Tarefas Concluídas
            </CardTitle>
          </CardHeader>
          <CardContent className="mt-auto">
            <div className="flex items-end justify-between mb-2">
              <p className="text-2xl font-bold">
                {overview?.tasks_completed ?? 0}/{overview?.tasks_total ?? 0}
              </p>
              <p className="text-xs text-muted-foreground mb-1">entregues</p>
            </div>
            <Progress
              value={
                overview && overview.tasks_total > 0
                  ? Math.round((overview.tasks_completed / overview.tasks_total) * 100)
                  : 0
              }
              className="h-2"
            />
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center gap-3 pb-2 space-y-0">
            <div className="p-2 bg-primary/10 text-primary rounded-lg">
              <FileText className="w-5 h-5" />
            </div>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Contratos
            </CardTitle>
          </CardHeader>
          <CardContent className="mt-auto">
            <div className="flex items-end justify-between mb-2">
              <p className="text-2xl font-bold">
                {overview?.contracts_signed ?? 0}/{overview?.contracts_total ?? 0}
              </p>
              <p className="text-xs text-muted-foreground mb-1">assinados</p>
            </div>
            <Progress
              value={
                overview && overview.contracts_total > 0
                  ? Math.round((overview.contracts_signed / overview.contracts_total) * 100)
                  : 0
              }
              className="h-2"
            />
          </CardContent>
        </Card>
      </div>

      {/* Contrato de Assessoria */}
      <PlannerContractSection
        contract={wedding.planner_contract}
        onEditContract={handleEditContract}
      />

      {/* Participantes & Contratantes do Evento */}
      <WeddingParticipantsSection
        participants={wedding.participants}
        onAddParticipant={() => setParticipantDialogOpen(true)}
        onRemoveParticipant={handleRemoveParticipant}
        isRemoving={removeParticipantMutation.isPending}
      />

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-4 border-b bg-muted/30">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-destructive" />
              <CardTitle className="text-base font-semibold">
                Ações Necessárias
              </CardTitle>
            </div>
            <Button variant="ghost" size="sm" className="h-8 gap-1" onClick={onNavigateToPlanning}>
              Ver planejamento <ArrowRight className="w-4 h-4" />
            </Button>
          </CardHeader>
          <CardContent className="p-6 flex-1">
            <UrgentTasksList tasks={urgentTasks} />
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-4 border-b bg-muted/30">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-primary" />
              <CardTitle className="text-base font-semibold">
                Próximos Vencimentos
              </CardTitle>
            </div>
            <Button variant="ghost" size="sm" className="h-8 gap-1" onClick={onNavigateToFinances}>
              Ver finanças <ArrowRight className="w-4 h-4" />
            </Button>
          </CardHeader>
          <CardContent className="p-6 flex-1">
            <UpcomingInstallmentsList installments={upcomingInstallments} />
          </CardContent>
        </Card>
      </div>

      {contractDialogOpen && (
        <PlannerContractDialog
          weddingUuid={wedding.uuid}
          contract={wedding.planner_contract}
          open={contractDialogOpen}
          onOpenChange={setContractDialogOpen}
        />
      )}

      {participantDialogOpen && (
        <AddParticipantDialog
          weddingUuid={wedding.uuid}
          open={participantDialogOpen}
          onOpenChange={setParticipantDialogOpen}
        />
      )}
    </div>
  );
}
