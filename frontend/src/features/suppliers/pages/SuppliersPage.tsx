import { getApiErrorInfo } from "@/api/error-utils";
import {
  ListPageErrorState,
  ListPageLoadingState,
} from "@/features/shared/components/PageState";

import { DeleteSupplierDialog } from "../components/DeleteSupplierDialog";
import { SupplierFormDialog } from "../components/SupplierFormDialog";
import { SuppliersTable } from "../components/SuppliersTable";
import { useSuppliersPage } from "../hooks/useSuppliersPage";
import type { SupplierStatusFilter } from "../types";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { AlertCircle, Plus, Search } from "lucide-react";

export default function SuppliersPage() {
  const {
    search,
    setSearch,
    statusFilter,
    setStatusFilter,
    formOpen,
    setFormOpen,
    formMode,
    formState,
    setFormState,
    supplierToDelete,
    setSupplierToDelete,
    filteredSuppliers,
    totalCount,
    isLoading,
    error,
    refetch,
    isSaving,
    isDeleting,
    openCreateDialog,
    openEditDialog,
    handleSaveSupplier,
    handleDeleteSupplier,
  } = useSuppliersPage();

  if (isLoading) {
    return <ListPageLoadingState />;
  }

  if (error) {
    const { message } = getApiErrorInfo(
      error,
      "Não foi possível carregar a lista de fornecedores.",
    );

    return <ListPageErrorState message={message} onRetry={refetch} />;
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Fornecedores</h2>
          <p className="text-muted-foreground">
            Gerencie o cadastro global de fornecedores da sua operação.
          </p>
        </div>
        <Button onClick={openCreateDialog}>
          <Plus className="mr-2 h-4 w-4" />
          Novo Fornecedor
        </Button>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por nome, e-mail, telefone ou CNPJ..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="pl-9"
          />
        </div>

        <Select
          value={statusFilter}
          onValueChange={(value: SupplierStatusFilter) => setStatusFilter(value)}
        >
          <SelectTrigger className="w-full md:w-50">
            <SelectValue placeholder="Filtrar por status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos os status</SelectItem>
            <SelectItem value="active">Ativos</SelectItem>
            <SelectItem value="inactive">Inativos</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            {filteredSuppliers.length} de {totalCount} fornecedores
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredSuppliers.length === 0 ? (
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
            <SuppliersTable
              suppliers={filteredSuppliers}
              onEdit={openEditDialog}
              onDelete={setSupplierToDelete}
            />
          )}
        </CardContent>
      </Card>

      <SupplierFormDialog
        open={formOpen}
        mode={formMode}
        formState={formState}
        setFormState={setFormState}
        isSaving={isSaving}
        onOpenChange={setFormOpen}
        onSave={handleSaveSupplier}
      />

      <DeleteSupplierDialog
        supplier={supplierToDelete}
        isDeleting={isDeleting}
        onCancel={() => setSupplierToDelete(null)}
        onConfirm={handleDeleteSupplier}
      />
    </div>
  );
}
