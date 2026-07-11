import { useWeddingsPage } from "../hooks/useWeddingsPage";
import { WeddingsTable } from "../components/WeddingsTable";
import { WeddingFilters } from "../components/WeddingFilters";
import { CreateWeddingDialog } from "../components/CreateWeddingDialog";
import { EmptyWeddingsState } from "../components/EmptyWeddingsState";
import {
  ListPageErrorState,
  ListPageLoadingState,
} from "@/components/page-states";
import { DataPagination } from "@/components/data-pagination";
import { getApiErrorInfo } from "@/api/error-utils";
import { getDashboardSummaryQueryKey } from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
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
    isFetching,
    error,
    refetch,
    pagination,
  } = useWeddingsPage();

  const queryClient = useQueryClient();

  if (error) {
    const { message } = getApiErrorInfo(
      error,
      "Não foi possível carregar a lista de casamentos.",
    );

    return <ListPageErrorState message={message} onRetry={refetch} />;
  }

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl sm:text-3xl font-bold tracking-tight">
            Casamentos
          </h1>
          <p className="text-muted-foreground mt-1">
            Gerencie e acompanhe todos os eventos ativos.
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <Plus className="mr-2 size-4" />
          Novo Casamento
        </Button>
      </div>

      <WeddingFilters
        search={search}
        onSearchChange={setSearch}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
      />

      <div className="bg-card rounded-xl border shadow-soft overflow-hidden">
        {isLoading ? (
          <ListPageLoadingState />
        ) : filteredWeddings.length === 0 && totalCount === 0 ? (
          <EmptyWeddingsState
            onCreateClick={() => setCreateDialogOpen(true)}
          />
        ) : filteredWeddings.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold">
              Nenhum casamento encontrado
            </h3>
            <p className="text-sm text-muted-foreground mt-2">
              Tente ajustar os filtros de busca
            </p>
          </div>
        ) : (
          <>
            <WeddingsTable
              weddings={filteredWeddings}
              onRefetch={refetch}
              pageSize={pagination.pageSize}
            />
            <DataPagination
              from={pagination.info.from}
              to={pagination.info.to}
              totalCount={totalCount}
              totalPages={pagination.info.totalPages}
              currentPage={pagination.info.page}
              hasPrevious={pagination.info.hasPrevious}
              hasNext={pagination.info.hasNext}
              isFetching={isFetching}
              onPrevious={pagination.previousPage}
              onNext={pagination.nextPage}
              onGoToPage={pagination.goToPage}
            />
          </>
        )}
      </div>

      <CreateWeddingDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onSuccess={() => {
          refetch();
          queryClient.invalidateQueries({
            queryKey: getDashboardSummaryQueryKey(),
          });
          setCreateDialogOpen(false);
        }}
      />
    </div>
  );
}
