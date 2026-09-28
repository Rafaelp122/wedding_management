import { lazy, Suspense, useState } from "react";
import { getApiErrorInfo } from "@/api/error-utils";
import {
  ListPageErrorState,
  ListPageLoadingState,
} from "@/components/page-states";

import { SupplierFormDialog } from "../components/suppliers/SupplierFormDialog";
import { SuppliersTable } from "../components/suppliers/SuppliersTable";
import { ConfirmDeleteDialog } from "@/components/ui/confirm-delete-dialog";
import { DataPagination } from "@/components/data-pagination";
import { useSuppliersPage } from "../hooks/useSuppliersPage";
import type { SupplierStatusFilter } from "../types";

import { PageContainer } from "@/components/layouts/PageContainer";
import { PageHeader } from "@/components/layouts/PageHeader";
import { PageFilterBar } from "@/components/layouts/PageFilterBar";
import { PageCardContainer } from "@/components/layouts/PageCardContainer";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { AlertCircle, Plus } from "lucide-react";

const SupplierDetailDialog = lazy(
  () =>
    import("../components/suppliers/SupplierDetailDialog").then((m) => ({
      default: m.SupplierDetailDialog,
    })),
);

export default function SuppliersPage() {
  const [detailUuid, setDetailUuid] = useState<string | null>(null);

  const {
    search,
    setSearch,
    statusFilter,
    setStatusFilter,
    formOpen,
    setFormOpen,
    formMode,
    editingSupplier,
    supplierToDelete,
    setSupplierToDelete,
    filteredSuppliers,
    totalCount,
    isLoading,
    isFetching,
    error,
    refetch,
    isDeleting,
    openCreateDialog,
    openEditDialog,
    handleDeleteSupplier,
    pagination,
  } = useSuppliersPage();

  if (error) {
    const { message } = getApiErrorInfo(
      error,
      "Não foi possível carregar a lista de fornecedores.",
    );

    return <ListPageErrorState message={message} onRetry={refetch} />;
  }

  return (
    <PageContainer>
      <PageHeader
        title="Fornecedores"
        description="Gerencie o cadastro global de fornecedores da sua operação."
        actions={
          <Button onClick={openCreateDialog}>
            <Plus className="mr-2 h-4 w-4" />
            Novo Fornecedor
          </Button>
        }
      />

      <PageFilterBar
        search={search}
        onSearchChange={(value) => setSearch(value)}
        searchPlaceholder="Buscar por nome, e-mail, telefone ou CNPJ..."
      >
        <Select
          value={statusFilter}
          onValueChange={(value: SupplierStatusFilter) => setStatusFilter(value)}
        >
          <SelectTrigger className="w-full sm:w-50" aria-label="Filtrar por status">
            <SelectValue placeholder="Filtrar por status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos os status</SelectItem>
            <SelectItem value="active">Ativos</SelectItem>
            <SelectItem value="inactive">Inativos</SelectItem>
          </SelectContent>
        </Select>
      </PageFilterBar>

      <PageCardContainer>
        <div className="px-6 py-4 border-b border-border">
          <h3 className="text-base font-semibold text-foreground">
            {isLoading ? "Carregando..." : `${filteredSuppliers.length} de ${totalCount} fornecedores`}
          </h3>
        </div>
        <div className="p-6">
          {isLoading ? (
            <ListPageLoadingState />
          ) : filteredSuppliers.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle className="mb-4 h-12 w-12 text-muted-foreground" />
              <h3 className="text-lg font-semibold">Nenhum fornecedor encontrado</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {search || statusFilter !== "all"
                  ? "Tente ajustar os filtros de busca"
                  : "Clique em 'Novo Fornecedor' para começar"}
              </p>
            </div>
          ) : (
            <>
              <SuppliersTable
                suppliers={filteredSuppliers}
                onEdit={openEditDialog}
                onDelete={setSupplierToDelete}
                onDetail={setDetailUuid}
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
      </PageCardContainer>

      <SupplierFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        mode={formMode}
        supplier={editingSupplier}
        onSuccess={() => refetch()}
      />

      <ConfirmDeleteDialog
        open={!!supplierToDelete}
        onOpenChange={(open) => {
          if (!open) setSupplierToDelete(null);
        }}
        title="Excluir fornecedor"
        description="Esta ação não pode ser desfeita."
        itemName={supplierToDelete?.name || ""}
        onConfirm={handleDeleteSupplier}
        isPending={isDeleting}
      />

      <Suspense fallback={null}>
        <SupplierDetailDialog
          supplierUuid={detailUuid}
          open={!!detailUuid}
          onOpenChange={(open) => {
            if (!open) setDetailUuid(null);
          }}
        />
      </Suspense>
    </PageContainer>
  );
}
