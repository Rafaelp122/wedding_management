import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { X } from "lucide-react";

import type { InstallmentOut } from "@/api/generated/v1/models/installmentOut";
import { formatCurrencyBR } from "@/lib/formatters";

import { TableCell, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

import { installmentStatusBadge } from "./constants";

interface ExpenseInstallmentRowProps {
  installment: InstallmentOut;
  isPaying: boolean;
  onTogglePayment: (uuid: string, isPaid: boolean) => void;
}

export function ExpenseInstallmentRow({
  installment,
  isPaying,
  onTogglePayment,
}: ExpenseInstallmentRowProps) {
  const st = installmentStatusBadge[installment.status] ?? {
    variant: "outline" as const,
    label: installment.status,
    icon: null,
  };
  const isPaid = installment.status === "PAID";

  return (
    <TableRow key={installment.uuid}>
      <TableCell className="font-medium text-xs">
        {installment.installment_number}
      </TableCell>
      <TableCell className="text-sm">
        R$ {formatCurrencyBR(Number(installment.amount))}
      </TableCell>
      <TableCell className="text-xs text-muted-foreground">
        {format(new Date(installment.due_date), "dd/MM/yyyy", {
          locale: ptBR,
        })}
      </TableCell>
      <TableCell>
        <Badge variant={st.variant} className="text-[10px] h-5">
          {st.icon}
          {st.label}
        </Badge>
      </TableCell>
      <TableCell>
        <Button
          size="sm"
          variant={isPaid ? "destructive" : "outline"}
          className="h-7 text-xs"
          onClick={() => onTogglePayment(installment.uuid, isPaid)}
          disabled={isPaying}
        >
          {isPaid ? (
            <>
              <X className="size-3 mr-0.5" />
              Desmarcar
            </>
          ) : (
            "Marcar como Pago"
          )}
        </Button>
      </TableCell>
    </TableRow>
  );
}
