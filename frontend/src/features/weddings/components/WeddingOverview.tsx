import {
  CalendarHeart,
  Wallet,
  CheckSquare,
  Store,
  AlertCircle,
  Clock,
  ArrowRight,
  Heart,
} from "lucide-react";
import { Link } from "react-router-dom";
import type { WeddingOut } from "@/api/generated/v1/models";
import { useFinancesBudgetsForWedding } from "@/api/generated/v1/endpoints/finances/finances";
import { useSchedulerTasksList } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { useLogisticsSuppliersList } from "@/api/generated/v1/endpoints/logistics/logistics";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { getWeddingStatusInfo } from "../utils/weddingStatus";

interface WeddingOverviewProps {
  wedding: WeddingOut;
}

export function WeddingOverview({ wedding }: WeddingOverviewProps) {
  const statusInfo = getWeddingStatusInfo(wedding.status);

  // Fetching data for metrics
  const { data: budgetResponse } = useFinancesBudgetsForWedding(wedding.uuid);
  const { data: tasksResponse } = useSchedulerTasksList({
    wedding_id: wedding.uuid,
  });
  const { data: suppliersResponse } = useLogisticsSuppliersList();

  const budget = budgetResponse?.data;
  const tasks = tasksResponse?.data?.items || [];
  const suppliers = suppliersResponse?.data?.items || [];

  // Derived metrics
  const today = new Date();
  const eventDate = new Date(wedding.date);
  const diffTime = eventDate.getTime() - today.getTime();
  const daysRemaining = Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));

  const budgetPercentage =
    budget && Number(budget.total_estimated) > 0
      ? Math.min(
          100,
          Math.max(
            0,
            Math.round(
              (Number(budget.total_overall_spent || 0) /
                Number(budget.total_estimated)) *
                100,
            ),
          ),
        )
      : 0;

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((t) => t.is_completed).length;
  const tasksPercentage =
    totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const totalSuppliers = suppliers.length;
  const signedSuppliers = suppliers.filter((s) => s.is_active).length;
  const suppliersPercentage =
    totalSuppliers > 0
      ? Math.round((signedSuppliers / totalSuppliers) * 100)
      : 0;

  const urgentTasks = tasks
    .filter((t) => !t.is_completed)
    .sort((a, b) => {
      const dateA = a.due_date ? new Date(a.due_date).getTime() : Infinity;
      const dateB = b.due_date ? new Date(b.due_date).getTime() : Infinity;
      return dateA - dateB;
    })
    .slice(0, 3);

  // Temporary mock for upcoming payments as they are not yet fully available in a consolidated way
  const upcomingPayments: Array<{
    id: string;
    supplier: string;
    description: string;
    amount: number;
    dueDate: string;
  }> = [];

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* Header com nomes e status */}
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
            }).format(eventDate)}{" "}
            • {wedding.location}
          </p>
        </div>
        <Badge variant={statusInfo.variant} className="w-fit text-sm py-1 px-3">
          {statusInfo.label}
        </Badge>
      </div>

      {/* Top Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Days Remaining */}
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
            <div className="text-3xl font-bold">{daysRemaining}</div>
            <p className="text-xs text-muted-foreground mt-1">
              dias para o grande dia
            </p>
          </CardContent>
        </Card>

        {/* Budget Health */}
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
              <p className="text-2xl font-bold">{budgetPercentage}%</p>
              <p className="text-xs text-muted-foreground mb-1">utilizado</p>
            </div>
            <Progress value={budgetPercentage} className="h-2" />
          </CardContent>
        </Card>

        {/* Tasks Progress */}
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
                {completedTasks}/{totalTasks}
              </p>
              <p className="text-xs text-muted-foreground mb-1">entregues</p>
            </div>
            <Progress value={tasksPercentage} className="h-2" />
          </CardContent>
        </Card>

        {/* Suppliers Status */}
        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center gap-3 pb-2 space-y-0">
            <div className="p-2 bg-primary/10 text-primary rounded-lg">
              <Store className="w-5 h-5" />
            </div>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Fornecedores
            </CardTitle>
          </CardHeader>
          <CardContent className="mt-auto">
            <div className="flex items-end justify-between mb-2">
              <p className="text-2xl font-bold">
                {signedSuppliers}/{totalSuppliers}
              </p>
              <p className="text-xs text-muted-foreground mb-1">contratados</p>
            </div>
            <Progress value={suppliersPercentage} className="h-2" />
          </CardContent>
        </Card>
      </div>

      {/* Two Column Layout for Actionable Items */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Urgent Actions */}
        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-4 border-b bg-muted/30">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-destructive" />
              <CardTitle className="text-base font-semibold">
                Ações Necessárias
              </CardTitle>
            </div>
            <Button asChild variant="ghost" size="sm" className="h-8 gap-1">
              <Link to="#">
                Ver planejamento <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="p-6 flex-1">
            {urgentTasks.length > 0 ? (
              <div className="space-y-4">
                {urgentTasks.map((task) => (
                  <div
                    key={task.uuid}
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

        {/* Right Column: Upcoming Payments */}
        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-4 border-b bg-muted/30">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-primary" />
              <CardTitle className="text-base font-semibold">
                Próximos Vencimentos
              </CardTitle>
            </div>
            <Button asChild variant="ghost" size="sm" className="h-8 gap-1">
              <Link to="#">
                Ver finanças <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="p-6 flex-1">
            {upcomingPayments.length > 0 ? (
              <div className="space-y-4">
                {upcomingPayments.map((payment) => (
                  <div
                    key={payment.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors"
                  >
                    <div>
                      <p className="text-sm font-medium">{payment.supplier}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {payment.description}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">
                        {formatCurrency(payment.amount)}
                      </p>
                      <p className="text-xs text-orange-500 mt-0.5 font-medium">
                        {new Intl.DateTimeFormat("pt-BR", {
                          day: "2-digit",
                          month: "short",
                        }).format(new Date(payment.dueDate))}
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

// Importing Button locally since it was used in the mockup
import { Button } from "@/components/ui/button";
