import { useState } from "react";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { WeddingsTable } from "../components/WeddingsTable";
import { WeddingFilters } from "../components/WeddingFilters";
import { CreateWeddingDialog } from "../components/CreateWeddingDialog";
import { getApiErrorInfo } from "@/api/error-utils";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, Plus } from "lucide-react";

export default function WeddingsListPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  // Fetch weddings com React Query (gerado pelo Orval)
  const { data, isLoading, error, refetch } = useWeddingsList();

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  // Error state
  if (error) {
    const { message } = getApiErrorInfo(
      error,
      "Não foi possível carregar a lista de casamentos.",
    );

    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erro ao carregar dados</AlertTitle>
        <AlertDescription>
          {message}
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            className="mt-4"
          >
            Tentar Novamente
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  // Extrair dados da paginação
  const weddings = data?.data.items ?? [];
  const totalCount = data?.data.count ?? 0;

  // Filtrar localmente (busca e status)
  const filteredWeddings = weddings.filter((wedding) => {
    const matchesSearch =
      search === "" ||
      wedding.groom_name.toLowerCase().includes(search.toLowerCase()) ||
      wedding.bride_name.toLowerCase().includes(search.toLowerCase()) ||
      wedding.location.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "all" || wedding.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Casamentos</h2>
          <p className="text-muted-foreground">
            Gerencie todos os seus eventos de casamento
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Novo Casamento
        </Button>
      </div>

      {/* Filtros */}
      <WeddingFilters
        search={search}
        onSearchChange={setSearch}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
      />

      {/* Card com tabela */}
      <Card>
        <CardHeader>
          <CardTitle>
            {filteredWeddings.length} de {totalCount} casamentos
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredWeddings.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold">
                Nenhum casamento encontrado
              </h3>
              <p className="text-sm text-muted-foreground mt-2">
                {search || statusFilter !== "all"
                  ? "Tente ajustar os filtros de busca"
                  : "Clique em 'Novo Casamento' para começar"}
              </p>
            </div>
          ) : (
            <WeddingsTable weddings={filteredWeddings} onRefetch={refetch} />
          )}
        </CardContent>
      </Card>

      {/* Dialog de criar casamento */}
      <CreateWeddingDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onSuccess={() => {
          refetch();
          setCreateDialogOpen(false);
        }}
      />
    </div>
  );
}
