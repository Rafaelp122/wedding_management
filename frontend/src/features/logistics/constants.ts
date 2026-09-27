export {
  STATUS_STYLES,
  STATUS_LABELS,
  CONTRACT_STATUS_OPTIONS,
} from "@/features/contracts/constants";

export const ITEM_STATUS_STYLES: Record<string, string> = {
  PENDING: "bg-yellow-100 text-yellow-800 border-yellow-200",
  IN_PROGRESS: "bg-blue-100 text-blue-800 border-blue-200",
  DONE: "bg-green-100 text-green-800 border-green-200",
};

export const ITEM_STATUS_LABELS: Record<string, string> = {
  PENDING: "Pendente",
  IN_PROGRESS: "Em Andamento",
  DONE: "Concluído",
};

export const ACQUISITION_STATUS_OPTIONS = [
  { value: "PENDING", label: "Pendente" },
  { value: "IN_PROGRESS", label: "Em Andamento" },
  { value: "DONE", label: "Concluído" },
] as const;

export const SCOPE_STATUS_LABELS: Record<string, string> = {
  DESIRED: "Desejado",
  INCLUDED: "Incluído",
  DISCARDED: "Descartado",
};

export const INITIAL_SCOPE_OPTIONS = [
  { value: "INCLUDED", label: "Incluído" },
  { value: "DESIRED", label: "Desejado" },
] as const;


export const SCOPE_STATUS_STYLES: Record<string, string> = {
  DESIRED: "bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-950 dark:text-blue-200",
  INCLUDED: "bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-950 dark:text-emerald-200",
  DISCARDED: "bg-rose-100 text-rose-800 border-rose-200 dark:bg-rose-950 dark:text-rose-200",
};

export const DELIVERY_STATUS_LABELS: Record<string, string> = {
  PENDING: "Aguardando",
  DELIVERED: "Entregue",
  RETURNED: "Devolvido",
};

export const DELIVERY_STATUS_STYLES: Record<string, string> = {
  PENDING: "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-950 dark:text-amber-200",
  DELIVERED: "bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-950 dark:text-emerald-200",
  RETURNED: "bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300",
};

