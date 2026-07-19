import { lazy, Suspense } from "react";
import { AlertCircle, FileText, Package, Plus } from "lucide-react";

import { useWeddingVendorsItems } from "../hooks/useVendorsItems";
import { useVendorsItemsOrchestrator } from "../hooks/useVendorsItemsOrchestrator";
import { WeddingVendorsTable } from "./items/VendorsTable";
import { WeddingItemsTable } from "./items/ItemsTable";
import { CreateItemDialog } from "./items/CreateItemDialog";
import { EditItemDialog } from "./items/EditItemDialog";

import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";

const ContractDetailDialog = lazy(
  () =>
    import("./contracts/ContractDetailDialog").then((m) => ({
      default: m.ContractDetailDialog,
    })),
);

const ContractUploadDialog = lazy(
  () =>
    import("./contracts/ContractUploadDialog").then((m) => ({
      default: m.ContractUploadDialog,
    })),
);

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface WeddingVendorsItemsTabViewProps {
  weddingUuid: string;
  contracts: ContractOut[];
  items: ItemOut[];
  isLoading: boolean;
  error: unknown;
  detailContractUuid: string | null;
  setDetailContractUuid: (uuid: string | null) => void;
  uploadOpen: boolean;
  setUploadOpen: (open: boolean) => void;
  prefilledParentUuid: string | null;
  setPrefilledParentUuid: (uuid: string | null) => void;
  createItemOpen: boolean;
  setCreateItemOpen: (open: boolean) => void;
  editItem: ItemOut | null;
  setEditItem: (item: ItemOut | null) => void;
  refreshItems: () => void;
  handleCreateAddendum: (parentUuid: string) => void;
  handleNewContractClick: () => void;
}

export function WeddingVendorsItemsTabView({
  weddingUuid,
  contracts,
  items,
  isLoading,
  error,
  detailContractUuid,
  setDetailContractUuid,
  uploadOpen,
  setUploadOpen,
  prefilledParentUuid,
  setPrefilledParentUuid,
  createItemOpen,
  setCreateItemOpen,
  editItem,
  setEditItem,
  refreshItems,
  handleCreateAddendum,
  handleNewContractClick,
}: WeddingVendorsItemsTabViewProps) {
  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-[300px] w-full rounded-md" />
        <Skeleton className="h-[300px] w-full rounded-md" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Não foi possível carregar os dados de logística e fornecedores.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Contratos de Fornecedores
              </CardTitle>
              <CardDescription>
                Fornecedores e serviços vinculados formalmente a este evento.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="h-8 text-xs gap-1"
              onClick={handleNewContractClick}
            >
              <Plus className="size-3" />
              Novo Contrato
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <WeddingVendorsTable
            contracts={contracts}
            isAddendum={(c) => !!c.parent}
            onDetail={setDetailContractUuid}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5 text-primary" />
                Itens Logísticos
              </CardTitle>
              <CardDescription>
                Acompanhamento de recursos materiais, brindes e infraestrutura.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="h-8 text-xs gap-1"
              onClick={() => setCreateItemOpen(true)}
            >
              <Plus className="size-3" />
              Novo Item
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <WeddingItemsTable
            items={items}
            onEdit={setEditItem}
            onRefresh={refreshItems}
          />
        </CardContent>
      </Card>

      <Suspense fallback={null}>
        <ContractDetailDialog
          contractUuid={detailContractUuid}
          weddingUuid={weddingUuid}
          open={!!detailContractUuid}
          onOpenChange={(open) => {
            if (!open) setDetailContractUuid(null);
          }}
          onCreateAddendum={handleCreateAddendum}
        />
      </Suspense>

      <Suspense fallback={null}>
        <ContractUploadDialog
          weddingUuid={weddingUuid}
          open={uploadOpen}
          onOpenChange={setUploadOpen}
          onSuccess={() => {
            setUploadOpen(false);
            setPrefilledParentUuid(null);
          }}
          prefilledParentUuid={prefilledParentUuid}
        />
      </Suspense>

      <CreateItemDialog
        weddingUuid={weddingUuid}
        open={createItemOpen}
        onOpenChange={setCreateItemOpen}
        onSuccess={() => {
          setCreateItemOpen(false);
          refreshItems();
        }}
      />

      {editItem && (
        <EditItemDialog
          item={editItem}
          weddingUuid={weddingUuid}
          open={!!editItem}
          onOpenChange={(open) => {
            if (!open) setEditItem(null);
          }}
          onSuccess={() => {
            setEditItem(null);
            refreshItems();
          }}
        />
      )}
    </div>
  );
}

interface WeddingVendorsItemsTabProps {
  weddingUuid: string;
}

export function WeddingVendorsItemsTab({ weddingUuid }: WeddingVendorsItemsTabProps) {
  const { contracts, items, isLoading, error } = useWeddingVendorsItems(weddingUuid);
  const orchestrator = useVendorsItemsOrchestrator();

  return (
    <WeddingVendorsItemsTabView
      weddingUuid={weddingUuid}
      contracts={contracts}
      items={items}
      isLoading={isLoading}
      error={error}
      {...orchestrator}
    />
  );
}
