import { type ReactNode } from "react";
import { Check, AlertTriangle, Clock } from "lucide-react";

export const statusVariant: Record<string, "default" | "destructive" | "outline"> = {
  PAID: "default",
  SETTLED: "default",
  PARTIALLY_PAID: "outline",
  PENDING: "outline",
  OVERDUE: "destructive",
};

export const statusLabel: Record<string, string> = {
  PAID: "Pago",
  SETTLED: "Quitada",
  PARTIALLY_PAID: "Parcial",
  PENDING: "Pendente",
  OVERDUE: "Atrasado",
};

export const RECENT_EXPENSES_LIMIT = 10;

export const installmentStatusBadge: Record<
  string,
  {
    variant: "default" | "destructive" | "outline";
    label: string;
    icon: ReactNode;
  }
> = {
  PAID: {
    variant: "default",
    label: "Pago",
    icon: <Check className="size-3 mr-0.5" />,
  },
  PENDING: {
    variant: "outline",
    label: "Pendente",
    icon: <Clock className="size-3 mr-0.5" />,
  },
  OVERDUE: {
    variant: "destructive",
    label: "Atrasado",
    icon: <AlertTriangle className="size-3 mr-0.5" />,
  },
};
