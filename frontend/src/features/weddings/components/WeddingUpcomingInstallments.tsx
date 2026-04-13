"use client";

import { Clock } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useFinancesInstallmentsList } from "@/api/generated/v1/endpoints/finances/finances";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";
import { Skeleton } from "@/components/ui/skeleton";

interface WeddingUpcomingInstallmentsProps {
  weddingUuid: string;
}

export function WeddingUpcomingInstallments({
  weddingUuid,
}: WeddingUpcomingInstallmentsProps) {
  // Atualmente o endpoint de lista de parcelas não parece ter filtro por wedding_id no schema exposto
  // mas assumimos que a API filtra por contexto do usuário ou o parâmetro será adicionado.
  // Para este protótipo, vamos limitar a 5.
  const { data: response, isLoading } = useFinancesInstallmentsList({
    limit: 5,
  });

  const installments = response?.data?.items || [];
  // Filtramos as que pertencem a este casamento especificamente se o campo wedding bater com o UUID
  // ou confiamos no filtro do backend.
  const filteredInstallments = installments.filter(
    (i) => i.wedding === weddingUuid && i.status === "pending"
  );

  if (isLoading) {
    return <Skeleton className="h-[200px] w-full" />;
  }

  if (filteredInstallments.length === 0) {
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
          {filteredInstallments.map((installment) => (
            <div
              key={installment.uuid}
              className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">
                    Parcela #{installment.installment_number}
                  </span>
                  <Badge variant="outline" className="text-[10px] h-4">
                    Pendente
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Vence em {format(new Date(installment.due_date), "dd 'de' MMM", { locale: ptBR })}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold">
                  R$ {formatCurrencyBR(Number(installment.amount))}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
