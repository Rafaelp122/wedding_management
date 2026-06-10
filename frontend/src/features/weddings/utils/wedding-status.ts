type WeddingStatusBadgeVariant = "default" | "secondary" | "destructive";

interface WeddingStatusInfo {
  label: string;
  variant: WeddingStatusBadgeVariant;
}

interface WeddingStatusBadgeStyle {
  className: string;
  dotClassName?: string;
  icon?: "check";
}

interface WeddingStatusAvatarStyle {
  bg: string;
  border: string;
  text: string;
}

const DEFAULT_WEDDING_STATUS = "IN_PROGRESS";

const WEDDING_STATUS_INFO: Record<string, WeddingStatusInfo> = {
  IN_PROGRESS: { label: "Em Andamento", variant: "default" },
  COMPLETED: { label: "Concluído", variant: "secondary" },
  CANCELED: { label: "Cancelado", variant: "destructive" },
};

const WEDDING_STATUS_BADGE_STYLES: Record<string, WeddingStatusBadgeStyle> = {
  IN_PROGRESS: {
    className:
      "bg-aura-50 text-aura-700 border-aura-200 dark:bg-aura-500/10 dark:text-aura-400 dark:border-aura-500/20",
    dotClassName: "bg-aura-500",
  },
  COMPLETED: {
    className:
      "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20",
    icon: "check",
  },
  CANCELED: {
    className:
      "bg-red-50 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/20",
    dotClassName: "bg-red-500",
  },
};

const WEDDING_STATUS_AVATAR_STYLES: Record<string, WeddingStatusAvatarStyle> = {
  IN_PROGRESS: {
    bg: "bg-aura-100 dark:bg-aura-900/40",
    border: "border-aura-200 dark:border-aura-800/50",
    text: "text-aura-700 dark:text-aura-300",
  },
  COMPLETED: {
    bg: "bg-emerald-100 dark:bg-emerald-900/30",
    border: "border-emerald-200 dark:border-emerald-800/50",
    text: "text-emerald-700 dark:text-emerald-400",
  },
  CANCELED: {
    bg: "bg-red-100 dark:bg-red-900/30",
    border: "border-red-200 dark:border-red-800/50",
    text: "text-red-700 dark:text-red-400",
  },
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

export function getWeddingStatusBadgeStyle(status?: string): WeddingStatusBadgeStyle {
  if (!status) {
    return WEDDING_STATUS_BADGE_STYLES[DEFAULT_WEDDING_STATUS];
  }
  return WEDDING_STATUS_BADGE_STYLES[status] ?? WEDDING_STATUS_BADGE_STYLES[DEFAULT_WEDDING_STATUS];
}

export function getWeddingAvatarStyle(status?: string): WeddingStatusAvatarStyle {
  if (!status) {
    return WEDDING_STATUS_AVATAR_STYLES[DEFAULT_WEDDING_STATUS];
  }
  return WEDDING_STATUS_AVATAR_STYLES[status] ?? WEDDING_STATUS_AVATAR_STYLES[DEFAULT_WEDDING_STATUS];
}

export function getWeddingInitials(groomName: string, brideName: string): string {
  const first = groomName.trim().charAt(0).toUpperCase();
  const second = brideName.trim().charAt(0).toUpperCase();
  return `${first}&${second}`;
}

export type WeddingStatusFilter = "all" | "IN_PROGRESS" | "COMPLETED" | "CANCELED";
