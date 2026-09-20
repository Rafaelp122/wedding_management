import type { NotificationOut } from "@/api/generated/v1/models";

/**
 * Mapeia links de notificações para as rotas da aplicação.
 * Nota Arquitetural: Os atalhos para '/finances' são intencionalmente redirecionados
 * para '/weddings' enquanto o módulo de finanças for encapsulado como uma aba dentro do casamento.
 */
export const resolveNotificationRoute = (link: string): string => {
  if (!link) return "/dashboard";
  if (link.startsWith("/weddings/")) return link;
  if (link.startsWith("/weddings")) return "/weddings";
  if (link.startsWith("/finances")) return "/weddings";
  if (link.startsWith("/scheduler")) return "/scheduler";
  if (link.startsWith("/suppliers") || link.startsWith("/logistics")) return "/suppliers";
  if (link.startsWith("/settings")) return "/settings";
  if (link.startsWith("/dashboard")) return "/dashboard";
  return "/dashboard";
};

/**
 * Resolve a URL completa da entidade associada à notificação para redirecionamento.
 */
export const resolveEntityUrl = (notification: NotificationOut): string => {
  if (notification.wedding_id) {
    const targetType = notification.target_type;
    const targetId = notification.target_id;
    if (targetType === "installment" || targetType === "expense") {
      return `/weddings/${notification.wedding_id}?tab=finances${targetId ? `&expense_id=${targetId}` : ""}`;
    }
    if (targetType === "task") {
      return `/weddings/${notification.wedding_id}?tab=planning&subtab=checklist${targetId ? `&task_id=${targetId}` : ""}`;
    }
    if (targetType === "contract") {
      return `/weddings/${notification.wedding_id}?tab=logistics${targetId ? `&contract_id=${targetId}` : ""}`;
    }
    if (targetType === "wedding") {
      return `/weddings/${notification.wedding_id}`;
    }
  }

  if (notification.link) {
    return resolveNotificationRoute(notification.link);
  }

  return "/dashboard";
};
