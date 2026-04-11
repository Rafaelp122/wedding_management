type WeddingStatusBadgeVariant = "default" | "secondary" | "destructive";

interface WeddingStatusInfo {
  label: string;
  variant: WeddingStatusBadgeVariant;
}

const DEFAULT_WEDDING_STATUS = "IN_PROGRESS";

const WEDDING_STATUS_INFO: Record<string, WeddingStatusInfo> = {
  IN_PROGRESS: { label: "Em Andamento", variant: "default" },
  COMPLETED: { label: "Concluído", variant: "secondary" },
  CANCELED: { label: "Cancelado", variant: "destructive" },
};

export function getWeddingStatusInfo(status?: string): WeddingStatusInfo {
  if (!status) {
    return WEDDING_STATUS_INFO[DEFAULT_WEDDING_STATUS];
  }

  return WEDDING_STATUS_INFO[status] ?? WEDDING_STATUS_INFO[DEFAULT_WEDDING_STATUS];
}

export function getWeddingStatusLabel(status?: string): string {
  return getWeddingStatusInfo(status).label;
}
