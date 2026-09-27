import type { ContractAddendumOut } from "@/api/generated/v1/models/contractAddendumOut";

export type AddendumStatusFilter = "ALL" | "PENDING" | "SIGNED" | "CANCELED";

export const ADDENDUM_FILTER_OPTIONS: ReadonlyArray<{
  value: AddendumStatusFilter;
  label: string;
}> = [
  { value: "ALL", label: "Todos" },
  { value: "PENDING", label: "Pendentes" },
  { value: "SIGNED", label: "Assinados" },
  { value: "CANCELED", label: "Cancelados" },
];

/** Filtra aditivos por status (ALL retorna a lista intacta). */
export function filterAddendumsByStatus(
  addendums: ContractAddendumOut[],
  filter: AddendumStatusFilter,
): ContractAddendumOut[] {
  if (filter === "ALL") return addendums;
  return addendums.filter((a) => a.status === filter);
}

/** Converte "2500.00" em centavos inteiros (evita erro binário de float). */
export function amountToCents(amount: string | number | null | undefined): number {
  if (amount === null || amount === undefined) return 0;
  const num = typeof amount === "number" ? amount : Number.parseFloat(amount);
  if (!Number.isFinite(num)) return 0;
  return Math.round(num * 100);
}

/** Soma valores de aditivos com precisão de centavos. Retorna reais. */
export function sumAddendumAmounts(addendums: ContractAddendumOut[]): number {
  const totalCents = addendums.reduce((acc, a) => acc + amountToCents(a.amount), 0);
  return totalCents / 100;
}

/** Contagem de aditivos por status para os badges do filtro. */
export function countAddendumsByStatus(
  addendums: ContractAddendumOut[],
): Record<AddendumStatusFilter, number> {
  return {
    ALL: addendums.length,
    PENDING: addendums.filter((a) => a.status === "PENDING").length,
    SIGNED: addendums.filter((a) => a.status === "SIGNED").length,
    CANCELED: addendums.filter((a) => a.status === "CANCELED").length,
  };
}
