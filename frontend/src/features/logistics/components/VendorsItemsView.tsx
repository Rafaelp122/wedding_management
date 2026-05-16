import { useState } from "react";
import { AlertCircle, FileText, Package, Plus } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import { useWeddingVendorsItems } from "../hooks/useVendorsItems";
import { WeddingVendorsTable } from "./items/VendorsTable";
import { WeddingItemsTable } from "./items/ItemsTable";
import { ContractDetailDialog } from "./contracts/ContractDetailDialog";
import { ContractUploadDialog } from "./contracts/ContractUploadDialog";
import { CreateItemDialog } from "./items/CreateItemDialog";
import { EditItemDialog } from "./items/EditItemDialog";
import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import { getLogisticsItemsListQueryKey } from "@/api/generated/v1/endpoints/logistics/logistics";

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

interface WeddingVendorsItemsTabProps {
  weddingUuid: string;
}

export function WeddingVendorsItemsTab({ weddingUuid }: WeddingVendorsItemsTabProps) {
  const queryClient = useQueryClient();
  const { contracts, items, isLoading, error } = useWeddingVendorsItems(weddingUuid);

  const [detailContractUuid, setDetailContractUuid] = useState<string | null>(null);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [prefilledParentUuid, setPrefilledParentUuid] = useState<string | null>(null);
  const [createItemOpen, setCreateItemOpen] = useState(false);
  const [editItem, setEditItem] = useState<ItemOut | null>(null);

  const refreshItems = () => {
    queryClient.invalidateQueries({ queryKey: getLogisticsItemsListQueryKey() });
  };

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
              onClick={() => {
                setPrefilledParentUuid(null);
                setUploadOpen(true);
              }}
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

      <ContractDetailDialog
        contractUuid={detailContractUuid}
        weddingUuid={weddingUuid}
        open={!!detailContractUuid}
        onOpenChange={(open) => {
          if (!open) setDetailContractUuid(null);
        }}
        onCreateAddendum={(parentUuid) => {
          setPrefilledParentUuid(parentUuid);
          setUploadOpen(true);
          setDetailContractUuid(null);
        }}
      />

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
