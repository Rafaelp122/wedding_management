export const STATUS_STYLES: Record<string, string> = {
  DRAFT: "bg-gray-100 text-gray-700",
  PENDING: "bg-yellow-100 text-yellow-800",
  SIGNED: "bg-green-100 text-green-800",
  CANCELED: "bg-red-100 text-red-800",
};

export const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Rascunho",
  PENDING: "Pendente",
  SIGNED: "Assinado",
  CANCELED: "Cancelado",
};

export const CONTRACT_STATUS_OPTIONS = [
  { value: "DRAFT", label: "Rascunho" },
  { value: "PENDING", label: "Pendente" },
  { value: "SIGNED", label: "Assinado" },
  { value: "CANCELED", label: "Cancelado" },
] as const;
