import { useWeddingsPage } from "../hooks/useWeddingsPage";
import { WeddingsTable } from "../components/WeddingsTable";
import { WeddingFilters } from "../components/WeddingFilters";
import { CreateWeddingDialog } from "../components/CreateWeddingDialog";
import {
  ListPageErrorState,
  ListPageLoadingState,
} from "@/features/shared/components/PageState";
import { getApiErrorInfo } from "@/api/error-utils";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, Plus } from "lucide-react";

export default function WeddingsListPage() {
  const {
    search,
    setSearch,
    statusFilter,
    setStatusFilter,
    createDialogOpen,
    setCreateDialogOpen,
    filteredWeddings,
    totalCount,
    isLoading,
    error,
    refetch,
  } = useWeddingsPage();

  if (isLoading) {
    return <ListPageLoadingState />;
  }

  if (error) {
    const { message } = getApiErrorInfo(
      error,
      "Não foi possível carregar a lista de casamentos.",
    );

    return <ListPageErrorState message={message} onRetry={refetch} />;
  }

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
