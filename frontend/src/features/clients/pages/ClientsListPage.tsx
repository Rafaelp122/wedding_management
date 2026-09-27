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

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Users, Plus, Search } from "lucide-react";

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Users className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              Clientes & Contatos
            </h1>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Gestão unificada de noivos, contratantes financeiros e pessoas físicas do workspace.
          </p>
        </div>

        <Button onClick={handleOpenCreate} className="gap-2 shrink-0">
          <Plus className="h-4 w-4" />
          Novo Cliente
        </Button>
      </div>

      {/* Barra de Filtros e Busca */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por nome, CPF ou e-mail..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

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
    </div>
  );
}
