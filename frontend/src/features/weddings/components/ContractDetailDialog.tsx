import { useRef, useState, memo } from "react";
import { toast } from "sonner";
import {
  MessageCircle,
  Mail,
  Plus,
  Check,
  Upload,
  Loader2,
  X,
} from "lucide-react";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import {
  useLogisticsItemsList,
  useLogisticsItemsCreate,
  getLogisticsItemsListQueryKey,
  useLogisticsContractsRead,
  useLogisticsContractsList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { getApiErrorInfo } from "@/api/error-utils";
import { formatCurrencyBR, formatDateBR } from "@/features/shared/utils/formatters";
import { useQueryClient } from "@tanstack/react-query";
import { AXIOS_INSTANCE } from "@/api/axios-client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const STATUS_STYLES: Record<string, string> = {
  DRAFT: "bg-gray-100 text-gray-700",
  PENDING: "bg-yellow-100 text-yellow-800",
  SIGNED: "bg-green-100 text-green-800",
  CANCELED: "bg-red-100 text-red-800",
};

const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Rascunho",
  PENDING: "Pendente",
  SIGNED: "Assinado",
  CANCELED: "Cancelado",
};

const ITEM_STATUS_STYLES: Record<string, string> = {
  PENDING: "bg-yellow-100 text-yellow-800 border-yellow-200",
  IN_PROGRESS: "bg-blue-100 text-blue-800 border-blue-200",
  DONE: "bg-green-100 text-green-800 border-green-200",
};

const ITEM_STATUS_LABELS: Record<string, string> = {
  PENDING: "Pendente",
  IN_PROGRESS: "Em Andamento",
  DONE: "Concluído",
};

interface ContractDetailDialogProps {
  contractUuid: string | null;
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onExpenseClick?: (expenseUuid: string | null) => void;
  onGenerateExpense?: (contract: ContractOut) => void;
  onSupplierClick?: (supplierUuid: string) => void;
  onCreateAddendum?: (parentUuid: string) => void;
}

export const ContractDetailDialog = memo(function ContractDetailDialog({
  contractUuid,
  weddingUuid,
  open,
  onOpenChange,
  onExpenseClick,
  onGenerateExpense,
  onSupplierClick,
  onCreateAddendum,
}: ContractDetailDialogProps) {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isRemoving, setIsRemoving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [showInlineForm, setShowInlineForm] = useState(false);
  const [inlineName, setInlineName] = useState("");
  const [inlineQty, setInlineQty] = useState(1);
  const [inlineStatus, setInlineStatus] = useState("PENDING");

  const handleUpload = async () => {
    if (!selectedFile || !contractUuid) return;
    setIsUploading(true);
    const formData = new FormData();
    formData.append("pdf_file", selectedFile);
    try {
      await AXIOS_INSTANCE.post(
        `/api/v1/logistics/contracts/${contractUuid}/upload/`,
        formData,
      );
      toast.success("Documento enviado com sucesso!");
      queryClient.invalidateQueries({
        queryKey: ["/api/v1/logistics/contracts/"],
      });
    } catch (err) {
      console.error("Upload error:", err);
      toast.error("Erro ao enviar documento.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = async () => {
    if (!contractUuid) return;
    setIsRemoving(true);
    try {
      await AXIOS_INSTANCE.delete(
        `/api/v1/logistics/contracts/${contractUuid}/upload/`,
      );
      toast.success("Documento removido.");
      queryClient.invalidateQueries({
        queryKey: ["/api/v1/logistics/contracts/"],
      });
    } catch (err) {
      console.error("Remove file error:", err);
      toast.error("Erro ao remover documento.");
    } finally {
      setIsRemoving(false);
    }
  };

  const { data: contractResponse, isLoading: isContractLoading } =
    useLogisticsContractsRead(contractUuid ?? "", {
      query: { enabled: !!contractUuid, staleTime: 0 },
    });
  const contract = contractResponse?.data;

  const {
    data: itemsResponse,
    isLoading: isItemsLoading,
  } = useLogisticsItemsList({
    contract_id: contractUuid ?? "",
  } as Record<string, unknown>, {
    query: { enabled: !!contractUuid },
  });

  const { mutate: createItem, isPending: isCreatingItem } =
    useLogisticsItemsCreate();

  const items = itemsResponse?.data?.items ?? [];

  const { data: allContractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const addendums =
    allContractsResponse?.data?.items?.filter(
      (c) => c.parent === contractUuid,
    ) ?? [];

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
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[560px] max-h-[85vh] overflow-y-auto">
        {isContractLoading ? (
          <div className="space-y-3 py-4">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-4 w-40" />
          </div>
        ) : !contract ? (
          <DialogHeader>
            <DialogTitle>Contrato não encontrado</DialogTitle>
            <DialogDescription>
              Os dados deste contrato não estão disponíveis.
            </DialogDescription>
          </DialogHeader>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center justify-between pr-8">
                <span className="truncate">
                  {contract.name || contract.description || "Contrato"}
                </span>
                <Badge className={STATUS_STYLES[contract.status] || ""}>
                  {STATUS_LABELS[contract.status] || contract.status}
                </Badge>
              </DialogTitle>
          <DialogDescription asChild>
            <div className="space-y-1 pt-1">
              <p className="text-sm">
                Fornecedor:{" "}
                {onSupplierClick ? (
                  <button
                    type="button"
                    className="font-medium text-primary hover:underline cursor-pointer"
                    onClick={() => onSupplierClick(contract.supplier)}
                  >
                    {contract.supplier_name || contract.supplier.substring(0, 8)}
                  </button>
                ) : (
                  <span className="font-medium text-foreground">
                    {contract.supplier_name || contract.supplier.substring(0, 8)}
                  </span>
                )}
                <span className="inline-flex gap-1 ml-1">
                  {contract.supplier_phone && (
                    <a
                      href={`https://wa.me/55${contract.supplier_phone.replace(/\D/g, "")}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-green-600 hover:text-green-800"
                    >
                      <MessageCircle className="size-3.5" />
                    </a>
                  )}
                  {contract.supplier_email && (
                    <a
                      href={`mailto:${contract.supplier_email}`}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      <Mail className="size-3.5" />
                    </a>
                  )}
                </span>
              </p>
              {contract.signed_date && (
                <p className="text-sm">
                  Assinatura:{" "}
                  <span className="font-medium text-foreground">
                    {formatDateBR(contract.signed_date)}
                  </span>
                </p>
              )}
              <p className="text-sm">
                Valor Total:{" "}
                <span className="font-medium text-foreground">
                  R$ {formatCurrencyBR(Number(contract.total_amount))}
                </span>
              </p>
              {contract.description && (
                <p className="text-sm text-muted-foreground pt-1">
                  {contract.description}
                </p>
              )}
            </div>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Separator />

          {/* Documento */}
          <div>
            <h4 className="text-sm font-semibold mb-2">Documento</h4>
            {contract.has_file ? (
              <div className="rounded-lg border bg-muted/30 p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-muted-foreground">📎</span>
                    <span className="font-medium truncate max-w-[300px]">
                      {contract.file_name || "documento"}
                    </span>
                  </div>
                  <Button
                    variant="destructive"
                    size="sm"
                    className="h-7 text-xs"
                    onClick={handleRemoveFile}
                    disabled={isRemoving}
                  >
                    {isRemoving ? (
                      <Loader2 className="size-3 mr-1 animate-spin" />
                    ) : (
                      <X className="size-3 mr-1" />
                    )}
                    Remover
                  </Button>
                </div>
              </div>
            ) : (
              <div className="rounded-lg border bg-muted/30 p-3">
                <div className="flex items-center gap-2">
                  <Input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx,.doc,.xlsx,.xls,.png,.jpg,.jpeg,.txt"
                    className="flex-1 text-sm"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8 text-xs shrink-0"
                    onClick={handleUpload}
                    disabled={isUploading || !selectedFile}
                  >
                    {isUploading ? (
                      <Loader2 className="size-3 mr-1 animate-spin" />
                    ) : (
                      <Upload className="size-3 mr-1" />
                    )}
                    Enviar
                  </Button>
                </div>
                <p className="text-[11px] text-muted-foreground mt-1">
                  Formatos: PDF, Word, Excel, imagens
                </p>
              </div>
            )}
          </div>

          <Separator />

          {/* Itens vinculados */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold">Itens Vinculados</h4>
              <Button
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                onClick={() => setShowInlineForm(!showInlineForm)}
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
                  <Select
                    value={inlineStatus}
                    onValueChange={setInlineStatus}
                  >
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

            {isItemsLoading ? (
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
                      <th className="text-left px-3 py-2 font-medium text-xs">
                        Item
                      </th>
                      <th className="text-center px-3 py-2 font-medium text-xs w-16">
                        Qtd
                      </th>
                      <th className="text-right px-3 py-2 font-medium text-xs w-28">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((item: ItemOut) => (
                      <tr key={item.uuid} className="border-b last:border-0">
                        <td className="px-3 py-2 truncate max-w-[200px]">
                          {item.name}
                        </td>
                        <td className="px-3 py-2 text-center">
                          {item.quantity}
                        </td>
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

          <Separator />

          {/* Despesa vinculada */}
          <div>
            <h4 className="text-sm font-semibold mb-2">Despesa Vinculada</h4>
            {contract.has_linked_expense ? (
              <div className="rounded-lg border bg-muted/30 p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div>
                      <p className="text-sm font-medium">
                        R$ {formatCurrencyBR(Number(contract.total_amount))}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {contract.progress_percent || 0}% pago
                      </p>
                    </div>
                    <Progress
                      value={contract.progress_percent || 0}
                      className="h-2 w-20"
                    />
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs"
                    onClick={() => onExpenseClick?.(contract.expense_uuid ?? null)}
                  >
                    Ver detalhes da despesa →
                  </Button>
                </div>
              </div>
            ) : (
              <div className="rounded-lg border bg-muted/30 p-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">
                    Nenhuma despesa vinculada a este contrato.
                  </p>
                  {onGenerateExpense && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-7 text-xs"
                      onClick={() => onGenerateExpense(contract)}
                    >
                      Gerar Despesa
                    </Button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Aditivos */}
          {addendums.length > 0 && (
            <div>
              <Separator />
              <h4 className="text-sm font-semibold mb-2 mt-3">Aditivos</h4>
              <div className="rounded-md border">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left px-3 py-2 font-medium text-xs">Nome</th>
                      <th className="text-right px-3 py-2 font-medium text-xs w-24">Valor</th>
                      <th className="text-center px-3 py-2 font-medium text-xs w-20">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {addendums.map((a) => (
                      <tr key={a.uuid} className="border-b last:border-0">
                        <td className="px-3 py-2 truncate max-w-[180px]">{a.name || a.description || "Aditivo"}</td>
                        <td className="px-3 py-2 text-right">R$ {formatCurrencyBR(Number(a.total_amount))}</td>
                        <td className="px-3 py-2 text-center">
                          <Badge className={`text-[10px] h-5 ${STATUS_STYLES[a.status] || ""}`}>{STATUS_LABELS[a.status] || a.status}</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {onCreateAddendum && (
            <div className="mt-2">
              <Button
                variant="outline"
                size="sm"
                className="h-7 text-xs w-full"
                onClick={() => onCreateAddendum(contractUuid!)}
              >
                <Plus className="size-3 mr-1" />
                Criar Aditivo
              </Button>
            </div>
          )}
        </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
});
