import {
  CalendarHeart,
  Wallet,
  CheckSquare,
  FileText,
  AlertCircle,
  Clock,
  ArrowRight,
  Heart,
} from "lucide-react";
import { Link } from "react-router-dom";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import { useDashboardWedding } from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getWeddingStatusInfo } from "../utils/weddingStatus";

interface WeddingOverviewProps {
  wedding: WeddingOut;
}

export function WeddingOverview({ wedding }: WeddingOverviewProps) {
  const statusInfo = getWeddingStatusInfo(wedding.status);
  const { data } = useDashboardWedding(wedding.uuid);
  const overview = data?.data;

  const urgentTasks = overview?.urgent_tasks ?? [];
  const upcomingInstallments = overview?.upcoming_installments ?? [];

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
      maximumFractionDigits: 0,
    }).format(value);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            {wedding.groom_name} & {wedding.bride_name}
          </h2>
          <p className="text-muted-foreground mt-1">
            {new Intl.DateTimeFormat("pt-BR", {
              day: "2-digit",
              month: "long",
              year: "numeric",
            }).format(new Date(wedding.date))}{" "}
            • {wedding.location}
          </p>
        </div>
        <Badge variant={statusInfo.variant} className="w-fit text-sm py-1 px-3">
          {statusInfo.label}
        </Badge>
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
            <Button asChild variant="ghost" size="sm" className="h-8 gap-1">
              <Link to={`/weddings/${wedding.uuid}?tab=planning&subtab=checklist`}>
                Ver planejamento <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="p-6 flex-1">
            {urgentTasks.length > 0 ? (
              <div className="space-y-4">
                {urgentTasks.map((task) => (
                  <div
                    key={`${task.title}-${task.due_date ?? ""}`}
                    className="flex items-start gap-4 p-4 rounded-lg border border-destructive/20 bg-destructive/5"
                  >
                    <div className="mt-0.5">
                      <div className="w-5 h-5 rounded border-2 border-destructive/30 flex items-center justify-center bg-background" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">{task.title}</p>
                      <p className="text-xs text-destructive mt-1 font-medium">
                        Prioridade: Alta
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-muted-foreground py-8">
                <Heart className="w-8 h-8 text-muted/30 mb-3" />
                <p className="text-sm">Tudo em dia por aqui!</p>
              </div>
            )}
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
            <Button asChild variant="ghost" size="sm" className="h-8 gap-1">
              <Link to={`/weddings/${wedding.uuid}?tab=finances`}>
                Ver finanças <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="p-6 flex-1">
            {upcomingInstallments.length > 0 ? (
              <div className="space-y-4">
                {upcomingInstallments.map((inst) => (
                  <div
                    key={inst.installment_number}
                    className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors"
                  >
                    <div>
                      <p className="text-sm font-medium">
                        Parcela #{inst.installment_number}
                      </p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {new Intl.DateTimeFormat("pt-BR", {
                          day: "2-digit",
                          month: "short",
                        }).format(new Date(inst.due_date))}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">
                        {formatCurrency(inst.amount)}
                      </p>
                      <p className="text-xs text-orange-500 mt-0.5 font-medium">
                        {inst.status === "OVERDUE" ? "Atrasado" : "Pendente"}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-muted-foreground py-8">
                <Wallet className="w-8 h-8 text-muted/30 mb-3" />
                <p className="text-sm">Nenhum pagamento próximo.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
