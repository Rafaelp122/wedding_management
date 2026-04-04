import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { StatsCards } from "@/features/dashboard/components/StatsCards";
import { getApiErrorInfo } from "@/api/error-utils";

import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RecentWeddings } from "@/features/dashboard/components/RecentWeddings";

export default function DashboardPage() {
  // 1. Busca os dados reais da API Django via Orval/React Query
  // O 'data' aqui é do tipo PaginatedWeddingList
  const { data, isLoading, error } = useWeddingsList();

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
        <Skeleton className="h-100 w-full" />
      </div>
    );
  }

  if (error) {
    const { message } = getApiErrorInfo(
      error,
      "Não foi possível carregar os dados do painel.",
    );

    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erro</AlertTitle>
        <AlertDescription>{message}</AlertDescription>
      </Alert>
    );
  }

  // 2. Extração correta dos dados da paginação do Django
  // 'count' é o total no banco, 'results' é o array de casamentos da página atual
  const totalInDatabase = data?.data.count ?? 0;
  const weddingsArray = data?.data.items ?? [];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          Bem-vindo ao seu painel de gestão de eventos.
        </p>
      </div>

      <StatsCards totalWeddings={totalInDatabase} />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Passamos o array real de casamentos (Wedding[]) para o componente */}
        <RecentWeddings weddings={weddingsArray} />

        {/* Placeholder para um gráfico ou calendário futuro */}
        <Card className="col-span-1 lg:col-span-3">
          <CardHeader>
            <CardTitle>Visão Geral</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-center h-50">
            <p className="text-sm text-muted-foreground italic text-center">
              Gráficos de desempenho financeiro virão aqui.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
