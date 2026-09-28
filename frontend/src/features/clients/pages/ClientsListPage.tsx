import { useState, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  useListClients,
  useDeleteClient,
  getListClientsQueryKey,
} from "@/api/generated/v1/endpoints/clients/clients";
import type { ClientOut } from "@/api/generated/v1/models/clientOut";

import { ClientsTable } from "../components/ClientsTable";
import { CreateClientDialog } from "../components/CreateClientDialog";
import { ConfirmDeleteDialog } from "@/components/ui/confirm-delete-dialog";
import {
  ListPageErrorState,
  ListPageLoadingState,
} from "@/components/page-states";

import { PageContainer } from "@/components/layouts/PageContainer";
import { PageHeader } from "@/components/layouts/PageHeader";
import { PageFilterBar } from "@/components/layouts/PageFilterBar";
import { Button } from "@/components/ui/button";
import { Users, Plus } from "lucide-react";

/**
 * Smart Component para a página de listagem geral de clientes (ADR-024).
 */
export default function ClientsListPage() {
  const [search, setSearch] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<ClientOut | null>(null);
  const [clientToDelete, setClientToDelete] = useState<ClientOut | null>(null);

  const queryClient = useQueryClient();

  const { data: clientsData, isLoading, error, refetch } = useListClients({
    q: search.trim() || undefined,
  });

  const deleteMutation = useDeleteClient({
    mutation: {
      onSuccess: () => {
        toast.success("Cliente removido com sucesso.");
        queryClient.invalidateQueries({ queryKey: getListClientsQueryKey() });
        setClientToDelete(null);
      },
      onError: (err: unknown) => {
        const errorMsg =
          (err as { response?: { data?: { detail?: string } } })?.response?.data
            ?.detail || "Erro ao excluir cliente. Verifique se ele possui vínculos.";
        toast.error(errorMsg);
      },
    },
  });

  const clients = useMemo(() => clientsData?.data?.items ?? [], [clientsData]);

  const handleOpenCreate = () => {
    setSelectedClient(null);
    setDialogOpen(true);
  };

  const handleOpenEdit = (client: ClientOut) => {
    setSelectedClient(client);
    setDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (!clientToDelete) return;
    deleteMutation.mutate({ uuid: clientToDelete.uuid });
  };

  if (isLoading) {
    return <ListPageLoadingState />;
  }

  if (error) {
    return (
      <ListPageErrorState
        message="Não foi possível buscar a lista de clientes da sua empresa."
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <PageContainer>
      {/* Header */}
      <PageHeader
        title={
          <div className="flex items-center gap-2">
            <Users className="h-6 w-6 text-primary" />
            <span>Clientes & Contatos</span>
          </div>
        }
        description="Gestão unificada de noivos, contratantes financeiros e pessoas físicas do workspace."
        actions={
          <Button onClick={handleOpenCreate} className="gap-2 shrink-0">
            <Plus className="h-4 w-4" />
            Novo Cliente
          </Button>
        }
      />

      {/* Barra de Filtros e Busca */}
      <PageFilterBar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Buscar por nome, CPF ou e-mail..."
      />

      {/* Tabela de Clientes */}
      <ClientsTable
        clients={clients}
        onEditClient={handleOpenEdit}
        onDeleteClient={(client) => setClientToDelete(client)}
        isDeleting={deleteMutation.isPending}
      />

      {/* Dialog de Criação / Edição */}
      <CreateClientDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        client={selectedClient}
      />

      {/* Dialog de Confirmação de Exclusão */}
      <ConfirmDeleteDialog
        open={Boolean(clientToDelete)}
        onOpenChange={(open) => !open && setClientToDelete(null)}
        title="Excluir Cliente"
        description="Esta ação removerá o cliente permanentemente."
        itemName={clientToDelete?.name ?? ""}
        onConfirm={handleConfirmDelete}
        isPending={deleteMutation.isPending}
      />
    </PageContainer>
  );
}
