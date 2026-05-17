import { MessageCircle, Mail, Phone } from "lucide-react";
import { memo } from "react";

import { useLogisticsSuppliersRead } from "@/api/generated/v1/endpoints/logistics/logistics";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import { formatDateBR } from "@/lib/formatters";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { Separator } from "@/components/ui/separator";

interface SupplierDetailDialogProps {
  supplierUuid: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const SupplierDetailDialog = memo(function SupplierDetailDialog({
  supplierUuid,
  open,
  onOpenChange,
}: SupplierDetailDialogProps) {
  const { data: response, isLoading, error } = useLogisticsSuppliersRead(
    supplierUuid ?? "",
    { query: { enabled: !!supplierUuid } },
  );

  const supplier: SupplierOut | undefined = response?.data;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[480px]">
        {isLoading ? (
          <div className="space-y-3 py-4">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-4 w-32" />
          </div>
        ) : error ? (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Não foi possível carregar os dados do fornecedor.
            </AlertDescription>
          </Alert>
        ) : !supplier ? (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Fornecedor não encontrado.
            </AlertDescription>
          </Alert>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle>{supplier.name}</DialogTitle>
            </DialogHeader>

            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <Badge variant={supplier.is_active ? "secondary" : "outline"}>
                  {supplier.is_active ? "Ativo" : "Inativo"}
                </Badge>
              </div>

              <Separator />

              <div className="grid grid-cols-1 gap-2">
                {supplier.email && (
                  <div className="flex items-center gap-2">
                    <Mail className="size-4 text-muted-foreground shrink-0" />
                    <a
                      href={`mailto:${supplier.email}`}
                      className="text-primary hover:underline truncate"
                    >
                      {supplier.email}
                    </a>
                  </div>
                )}

                {supplier.phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="size-4 text-muted-foreground shrink-0" />
                    <span className="text-foreground">{supplier.phone}</span>
                    <a
                      href={`https://wa.me/55${supplier.phone.replace(/\D/g, "")}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-green-600 hover:text-green-800"
                      title="Abrir WhatsApp"
                    >
                      <MessageCircle className="size-4" />
                    </a>
                  </div>
                )}

                {supplier.cnpj && (
                  <p className="text-muted-foreground">
                    CNPJ: {supplier.cnpj}
                  </p>
                )}
              </div>

              <Separator />

              <div>
                <p className="text-xs text-muted-foreground">
                  Cadastrado em: {formatDateBR(supplier.created_at)}
                </p>
                {supplier.updated_at !== supplier.created_at && (
                  <p className="text-xs text-muted-foreground">
                    Atualizado em: {formatDateBR(supplier.updated_at)}
                  </p>
                )}
              </div>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
});
