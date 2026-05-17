import { useState } from "react";
import { toast } from "sonner";
import { Plus, Check } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import {
  useLogisticsItemsCreate,
  getLogisticsItemsListQueryKey,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { getApiErrorInfo } from "@/api/error-utils";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

import {
  ITEM_STATUS_STYLES,
  ITEM_STATUS_LABELS,
} from "@/features/logistics/constants";

interface ContractItemsSectionProps {
  weddingUuid: string;
  contractUuid: string;
  items: ItemOut[];
  isLoading: boolean;
}

export function ContractItemsSection({
  weddingUuid,
  contractUuid,
  items,
  isLoading,
}: ContractItemsSectionProps) {
  const queryClient = useQueryClient();
  const { mutate: createItem, isPending: isCreatingItem } =
    useLogisticsItemsCreate();

  const [showInlineForm, setShowInlineForm] = useState(false);
  const [inlineName, setInlineName] = useState("");
  const [inlineQty, setInlineQty] = useState(1);
  const [inlineStatus, setInlineStatus] = useState("PENDING");

  const handleAddItem = () => {
    if (!inlineName.trim()) return;
    createItem(
      {
        data: {
          wedding: weddingUuid,
          contract: contractUuid,
          name: inlineName.trim(),
          quantity: inlineQty,
          acquisition_status: inlineStatus,
        },
      },
      {
        onSuccess: () => {
          toast.success("Item adicionado!");
          setShowInlineForm(false);
          setInlineName("");
          setInlineQty(1);
          setInlineStatus("PENDING");
          queryClient.invalidateQueries({
            queryKey: getLogisticsItemsListQueryKey(),
          });
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao criar item.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold">Itens Vinculados</h4>
        <Button
          variant="outline"
          size="sm"
          className="h-7 text-xs"
          onClick={() => setShowInlineForm((prev) => !prev)}
        >
          <Plus className="size-3 mr-1" />
          Adicionar Item
        </Button>
      </div>

      {showInlineForm && (
        <div className="rounded-md border bg-muted/30 p-3 mb-3 space-y-3">
          <Input
            placeholder="Nome do item"
            value={inlineName}
            onChange={(e) => setInlineName(e.target.value)}
            className="h-8 text-sm"
          />
          <div className="flex gap-2">
            <div className="w-20">
              <Input
                type="number"
                min={1}
                value={inlineQty}
                onChange={(e) =>
                  setInlineQty(Math.max(1, Number(e.target.value) || 1))
                }
                className="h-8 text-sm"
              />
            </div>
            <Select value={inlineStatus} onValueChange={setInlineStatus}>
              <SelectTrigger className="h-8 text-sm flex-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="PENDING">Pendente</SelectItem>
                <SelectItem value="IN_PROGRESS">Em Andamento</SelectItem>
                <SelectItem value="DONE">Concluído</SelectItem>
              </SelectContent>
            </Select>
            <Button
              size="sm"
              className="h-8 text-xs"
              onClick={handleAddItem}
              disabled={isCreatingItem || !inlineName.trim()}
            >
              <Check className="size-3 mr-1" />
              Salvar
            </Button>
          </div>
        </div>
      )}

      {isLoading ? (
        <Skeleton className="h-16 w-full" />
      ) : items.length === 0 ? (
        <p className="text-sm text-muted-foreground text-center py-3">
          Nenhum item vinculado a este contrato.
        </p>
      ) : (
        <div className="rounded-md border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="text-left px-3 py-2 font-medium text-xs">Item</th>
                <th className="text-center px-3 py-2 font-medium text-xs w-16">Qtd</th>
                <th className="text-right px-3 py-2 font-medium text-xs w-28">Status</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.uuid} className="border-b last:border-0">
                  <td className="px-3 py-2 truncate max-w-[200px]">{item.name}</td>
                  <td className="px-3 py-2 text-center">{item.quantity}</td>
                  <td className="px-3 py-2 text-right">
                    <Badge
                      className={`text-[10px] h-5 ${ITEM_STATUS_STYLES[item.acquisition_status] || ""}`}
                    >
                      {ITEM_STATUS_LABELS[item.acquisition_status] ||
                        item.acquisition_status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
