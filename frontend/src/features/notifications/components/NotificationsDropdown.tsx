import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import {
  Bell,
  CheckCheck,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { ConfirmDeleteDialog } from "@/components/ui/confirm-delete-dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  useNotificationsList,
  useNotificationsUnreadCount,
  useNotificationsMarkAsRead,
  useNotificationsMarkAllAsRead,
  useNotificationsDelete,
  useNotificationsBulkMarkAsRead,
  useNotificationsBulkDelete,
  useNotificationsClearAll,
  getNotificationsListQueryKey,
  getNotificationsUnreadCountQueryKey,
} from "@/api/generated/v1/endpoints/notifications/notifications";
import type { NotificationOut } from "@/api/generated/v1/models";
import { NotificationItem } from "./NotificationItem";

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

const ITEMS_PER_PAGE = 10;

export const NotificationsDropdown: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [page, setPage] = useState(1);
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isClearAllDialogOpen, setIsClearAllDialogOpen] = useState(false);

  const { data: notificationsResponse, isLoading } = useNotificationsList({
    offset: (page - 1) * ITEMS_PER_PAGE,
    limit: ITEMS_PER_PAGE,
  });

  const rawNotifications = notificationsResponse?.data?.items ?? [];
  const totalCount = notificationsResponse?.data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / ITEMS_PER_PAGE));

  const { data: unreadResponse } = useNotificationsUnreadCount();
  const unreadCount = unreadResponse?.data?.count ?? 0;

  const invalidateQueries = () => {
    queryClient.invalidateQueries({ queryKey: getNotificationsListQueryKey() });
    queryClient.invalidateQueries({ queryKey: getNotificationsUnreadCountQueryKey() });
  };

  const markAsRead = useNotificationsMarkAsRead({
    mutation: { onSuccess: invalidateQueries },
  });

  const markAllAsRead = useNotificationsMarkAllAsRead({
    mutation: { onSuccess: invalidateQueries },
  });

  const deleteNotification = useNotificationsDelete({
    mutation: { onSuccess: invalidateQueries },
  });

  const bulkMarkAsRead = useNotificationsBulkMarkAsRead({
    mutation: {
      onSuccess: () => {
        invalidateQueries();
        setSelectedIds(new Set());
      },
    },
  });

  const bulkDelete = useNotificationsBulkDelete({
    mutation: {
      onSuccess: () => {
        invalidateQueries();
        setSelectedIds(new Set());
      },
    },
  });

  const clearAll = useNotificationsClearAll({
    mutation: {
      onSuccess: () => {
        invalidateQueries();
        setSelectedIds(new Set());
        setIsClearAllDialogOpen(false);
        setIsSelectionMode(false);
        setPage(1);
      },
    },
  });

  const handleSelectNotification = (notification: NotificationOut) => {
    if (!notification.is_read) {
      markAsRead.mutate({ notificationId: notification.uuid });
    }
    const targetRoute = resolveEntityUrl(notification);
    navigate(targetRoute);
  };

  const handleMarkAsReadSingle = (notification: NotificationOut) => {
    markAsRead.mutate({ notificationId: notification.uuid });
  };

  const handleDeleteSingle = (notification: NotificationOut) => {
    deleteNotification.mutate({ notificationId: notification.uuid });
  };

  const handleMarkAllAsRead = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (unreadCount > 0) {
      markAllAsRead.mutate();
    }
  };

  const toggleSelectNotification = (notification: NotificationOut) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(notification.uuid)) {
        next.delete(notification.uuid);
      } else {
        next.add(notification.uuid);
      }
      return next;
    });
  };

  const handleToggleSelectAll = () => {
    if (selectedIds.size === rawNotifications.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(rawNotifications.map((n) => n.uuid)));
    }
  };

  const handleBulkMarkAsRead = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (selectedIds.size > 0) {
      bulkMarkAsRead.mutate({
        data: { notification_ids: Array.from(selectedIds) },
      });
    }
  };

  const handleBulkDelete = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (selectedIds.size > 0) {
      bulkDelete.mutate({
        data: { notification_ids: Array.from(selectedIds) },
      });
    }
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="relative text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 focus-visible:ring-primary/50 cursor-pointer"
            aria-label="Notificações"
          >
            <Bell aria-hidden="true" className="size-5" />
            {unreadCount > 0 && (
              <Badge
                variant="destructive"
                className="absolute -top-1 -right-1 size-5 p-0 flex items-center justify-center text-[10px] font-bold rounded-full border-2 border-background"
                aria-label={`${unreadCount} notificações não lidas`}
              >
                {unreadCount > 99 ? "99+" : unreadCount}
              </Badge>
            )}
          </Button>
        </DropdownMenuTrigger>

        <DropdownMenuContent align="end" className="w-80 sm:w-[480px] p-0 max-h-[85vh] flex flex-col">
          <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
            <div className="flex items-center gap-2">
              <DropdownMenuLabel className="p-0 font-semibold text-sm">
                Notificações
              </DropdownMenuLabel>
              {unreadCount > 0 && (
                <Badge variant="secondary" className="text-[10px] font-medium">
                  {unreadCount} novas
                </Badge>
              )}
            </div>

            <div className="flex items-center gap-1.5">
              {rawNotifications.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setIsSelectionMode(!isSelectionMode);
                    setSelectedIds(new Set());
                  }}
                  className="h-7 text-xs px-2 text-muted-foreground hover:text-foreground cursor-pointer"
                >
                  {isSelectionMode ? "Cancelar" : "Selecionar"}
                </Button>
              )}

              {!isSelectionMode && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleMarkAllAsRead}
                  disabled={unreadCount === 0 || markAllAsRead.isPending}
                  title={
                    unreadCount === 0
                      ? "Não há notificações pendentes para leitura"
                      : "Marcar todas como lidas"
                  }
                  className={
                    unreadCount === 0
                      ? "h-7 text-xs px-2 text-muted-foreground/40 opacity-60 cursor-not-allowed font-normal"
                      : "h-7 text-xs px-2 text-primary hover:text-primary/80 font-normal cursor-pointer"
                  }
                >
                  <CheckCheck className="size-3.5 mr-1" />
                  Marcar todas como lidas
                </Button>
              )}

              {!isSelectionMode && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (rawNotifications.length > 0) {
                      setIsClearAllDialogOpen(true);
                    }
                  }}
                  disabled={rawNotifications.length === 0}
                  title={
                    rawNotifications.length === 0
                      ? "Não há notificações para apagar"
                      : "Apagar todas as notificações"
                  }
                  aria-label="Apagar todas as notificações"
                  className={
                    rawNotifications.length === 0
                      ? "h-7 w-7 p-0 text-muted-foreground/40 opacity-60 cursor-not-allowed"
                      : "h-7 w-7 p-0 text-muted-foreground hover:text-destructive cursor-pointer"
                  }
                >
                  <Trash2 className="size-3.5" />
                </Button>
              )}
            </div>
          </div>

          {isSelectionMode && (
            <div className="flex items-center justify-between px-3.5 py-2.5 bg-muted/50 border-b border-border text-xs">
              <div className="flex items-center gap-2">
                <Checkbox
                  checked={rawNotifications.length > 0 && selectedIds.size === rawNotifications.length}
                  onCheckedChange={handleToggleSelectAll}
                  aria-label="Selecionar todas as notificações"
                />
                <span className="font-medium">
                  {selectedIds.size > 0 ? `${selectedIds.size} selecionada(s)` : "Selecionar todas"}
                </span>
              </div>

              {selectedIds.size > 0 && (
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleBulkMarkAsRead}
                    disabled={bulkMarkAsRead.isPending}
                    className="h-6 px-2 text-[11px] text-primary hover:text-primary/80 cursor-pointer"
                  >
                    <CheckCheck className="size-3 mr-1" />
                    Lidas
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleBulkDelete}
                    disabled={bulkDelete.isPending}
                    className="h-6 px-2 text-[11px] text-destructive hover:text-destructive/80 cursor-pointer"
                  >
                    <Trash2 className="size-3 mr-1" />
                    Excluir
                  </Button>
                </div>
              )}
            </div>
          )}

          <div className="overflow-y-auto max-h-96 p-2.5 flex flex-col gap-2">
            {isLoading ? (
              <div className="flex items-center justify-center p-6 text-muted-foreground text-xs gap-2">
                <Loader2 className="size-4 animate-spin" />
                Carregando notificações...
              </div>
            ) : rawNotifications.length === 0 ? (
              <div className="p-6 text-center text-xs text-muted-foreground">
                Você não tem novas notificações no momento.
              </div>
            ) : (
              rawNotifications.map((notification) => (
                <DropdownMenuItem
                  key={notification.uuid}
                  asChild
                  className="p-0 cursor-pointer focus:bg-transparent"
                >
                  <NotificationItem
                    notification={notification}
                    onSelect={handleSelectNotification}
                    onMarkAsRead={handleMarkAsReadSingle}
                    onDelete={handleDeleteSingle}
                    selectable={isSelectionMode}
                    selected={selectedIds.has(notification.uuid)}
                    onToggleSelect={toggleSelectNotification}
                  />
                </DropdownMenuItem>
              ))
            )}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-2 border-t border-border bg-card text-xs text-muted-foreground">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="h-7 text-xs px-2 gap-1 cursor-pointer disabled:opacity-40"
              >
                <ChevronLeft className="size-3.5" />
                Anterior
              </Button>

              <span className="font-medium">
                Página {page} de {totalPages}
              </span>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="h-7 text-xs px-2 gap-1 cursor-pointer disabled:opacity-40"
              >
                Próxima
                <ChevronRight className="size-3.5" />
              </Button>
            </div>
          )}
        </DropdownMenuContent>
      </DropdownMenu>

      <ConfirmDeleteDialog
        open={isClearAllDialogOpen}
        onOpenChange={setIsClearAllDialogOpen}
        title="Apagar todas as notificações?"
        description="Esta ação excluirá permanentemente todas as suas notificações da lista. Esta operação não pode ser desfeita."
        itemName="todas as notificações"
        requireTypedConfirmation={false}
        onConfirm={() => clearAll.mutate()}
        isPending={clearAll.isPending}
      />
    </>
  );
};
