"use client";

import { useState } from "react";
import { Clock, AlertTriangle, Check } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useFinancesInstallmentsList,
  useFinancesInstallmentsMarkAsPaid,
} from "@/api/generated/v1/endpoints/finances/finances";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";
import { getApiErrorInfo } from "@/api/error-utils";

interface WeddingUpcomingInstallmentsProps {
  weddingUuid: string;
}

export function WeddingUpcomingInstallments({
  weddingUuid,
}: WeddingUpcomingInstallmentsProps) {
  const queryClient = useQueryClient();
  const [payingUuid, setPayingUuid] = useState<string | null>(null);

  const { data: response, isLoading } = useFinancesInstallmentsList({
    wedding_id: weddingUuid,
  });

  const payMutation = useFinancesInstallmentsMarkAsPaid();

  const installments = (response?.data?.items || []).filter(
    (i) => i.status !== "PAID"
  );

  if (isLoading) {
    return <Skeleton className="h-[200px] w-full" />;
  }

  if (installments.length === 0) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Clock className="size-4 text-muted-foreground" />
            Próximos Vencimentos
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center py-6 text-muted-foreground">
          <p className="text-xs text-center">Nenhuma parcela pendente.</p>
        </CardContent>
      </Card>
    );
  }

  const handlePay = async (uuid: string) => {
    setPayingUuid(uuid);
    try {
      await payMutation.mutateAsync({ uuid });
      toast.success("Pagamento registrado com sucesso!");
      queryClient.invalidateQueries();
    } catch (error) {
      const { message } = getApiErrorInfo(error, "Erro ao registrar pagamento.");
      toast.error(message);
    } finally {
      setPayingUuid(null);
    }
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-sm font-semibold flex items-center gap-2">
          <Clock className="size-4 text-primary" />
          Próximos Vencimentos
        </CardTitle>
        <CardDescription className="text-xs">
          Compromissos financeiros agendados
        </CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y divide-border">
          {installments.map((installment) => {
            const isOverdue = installment.status === "OVERDUE";
            const isPaid = installment.status === "PAID";

            return (
              <div
                key={installment.uuid}
                className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">
                      Parcela #{installment.installment_number}
                    </span>
                    {isPaid ? (
                      <Badge
                        variant="default"
                        className="text-[10px] h-4 bg-green-100 text-green-700 hover:bg-green-100"
                      >
                        <Check className="size-3 mr-0.5" />
                        Pago
                      </Badge>
                    ) : isOverdue ? (
                      <Badge
                        variant="destructive"
                        className="text-[10px] h-4"
                      >
                        <AlertTriangle className="size-3 mr-0.5" />
                        Atrasado
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-[10px] h-4">
                        Pendente
                      </Badge>
                    )}
                  </div>
                  <p
                    className={`text-xs ${
                      isOverdue
                        ? "text-destructive font-medium"
                        : "text-muted-foreground"
                    }`}
                  >
                    {isPaid
                      ? `Pago em ${format(new Date(installment.paid_date!), "dd 'de' MMM", { locale: ptBR })}`
                      : `Vence em ${format(new Date(installment.due_date), "dd 'de' MMM", { locale: ptBR })}`}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-sm font-bold">
                      R$ {formatCurrencyBR(Number(installment.amount))}
                    </p>
                  </div>
                  {!isPaid ? (
                    <Button
                      size="sm"
                      variant={isOverdue ? "destructive" : "default"}
                      className="h-7 text-xs"
                      onClick={() => handlePay(installment.uuid)}
                      disabled={payingUuid === installment.uuid}
                    >
                      Pagar
                    </Button>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
