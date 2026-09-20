import React from "react";
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
import type { NotificationOut } from "@/api/generated/v1/models";
import { NotificationItem } from "./NotificationItem";

export interface NotificationsDropdownViewProps {
  page: number;
  totalPages: number;
  totalCount: number;
  unreadCount: number;
  notifications: NotificationOut[];
  isLoading: boolean;
  isSelectionMode: boolean;
  selectedIds: Set<string>;
  isClearAllDialogOpen: boolean;
  isMarkAllPending?: boolean;
  isBulkMarkAsReadPending?: boolean;
  isBulkDeletePending?: boolean;
  isClearAllPending?: boolean;
  onPageChange: (newPage: number) => void;
  onOpenClearAllDialogChange: (open: boolean) => void;
  onSelectNotification: (notification: NotificationOut) => void;
  onMarkAsReadSingle: (notification: NotificationOut) => void;
  onDeleteSingle: (notification: NotificationOut) => void;
  onMarkAllAsRead: (e: React.MouseEvent) => void;
  onToggleSelectionMode: () => void;
  onToggleSelectNotification: (notification: NotificationOut) => void;
  onToggleSelectAll: () => void;
  onBulkMarkAsRead: (e: React.MouseEvent) => void;
  onBulkDelete: (e: React.MouseEvent) => void;
  onOpenClearAllDialog: (e: React.MouseEvent) => void;
  onConfirmClearAll: () => void;
}

/**
 * Dumb Presenter Component para o dropdown de notificações.
 * Renderiza exclusivamente elementos visuais recebendo estado e callbacks via props.
 */
export const NotificationsDropdownView: React.FC<NotificationsDropdownViewProps> = ({
  page,
  totalPages,
  unreadCount,
  notifications,
  isLoading,
  isSelectionMode,
  selectedIds,
  isClearAllDialogOpen,
  isMarkAllPending = false,
  isBulkMarkAsReadPending = false,
  isBulkDeletePending = false,
  isClearAllPending = false,
  onPageChange,
  onOpenClearAllDialogChange,
  onSelectNotification,
  onMarkAsReadSingle,
  onDeleteSingle,
  onMarkAllAsRead,
  onToggleSelectionMode,
  onToggleSelectNotification,
  onToggleSelectAll,
  onBulkMarkAsRead,
  onBulkDelete,
  onOpenClearAllDialog,
  onConfirmClearAll,
}) => {
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
              {notifications.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onToggleSelectionMode}
                  className="h-7 text-xs px-2 text-muted-foreground hover:text-foreground cursor-pointer"
                >
                  {isSelectionMode ? "Cancelar" : "Selecionar"}
                </Button>
              )}

              {!isSelectionMode && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onMarkAllAsRead}
                  disabled={unreadCount === 0 || isMarkAllPending}
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
                  onClick={onOpenClearAllDialog}
                  disabled={notifications.length === 0}
                  title={
                    notifications.length === 0
                      ? "Não há notificações para apagar"
                      : "Apagar todas as notificações"
                  }
                  aria-label="Apagar todas as notificações"
                  className={
                    notifications.length === 0
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
                  checked={notifications.length > 0 && selectedIds.size === notifications.length}
                  onCheckedChange={onToggleSelectAll}
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
                    onClick={onBulkMarkAsRead}
                    disabled={isBulkMarkAsReadPending}
                    className="h-6 px-2 text-[11px] text-primary hover:text-primary/80 cursor-pointer"
                  >
                    <CheckCheck className="size-3 mr-1" />
                    Lidas
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onBulkDelete}
                    disabled={isBulkDeletePending}
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
            ) : notifications.length === 0 ? (
              <div className="p-6 text-center text-xs text-muted-foreground">
                Você não tem novas notificações no momento.
              </div>
            ) : (
              notifications.map((notification) => (
                <DropdownMenuItem
                  key={notification.uuid}
                  asChild
                  className="p-0 cursor-pointer focus:bg-transparent"
                >
                  <NotificationItem
                    notification={notification}
                    onSelect={onSelectNotification}
                    onMarkAsRead={onMarkAsReadSingle}
                    onDelete={onDeleteSingle}
                    selectable={isSelectionMode}
                    selected={selectedIds.has(notification.uuid)}
                    onToggleSelect={onToggleSelectNotification}
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
                onClick={() => onPageChange(Math.max(1, page - 1))}
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
                onClick={() => onPageChange(Math.min(totalPages, page + 1))}
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
        onOpenChange={onOpenClearAllDialogChange}
        title="Apagar todas as notificações?"
        description="Esta ação excluirá permanentemente todas as suas notificações da lista. Esta operação não pode ser desfeita."
        itemName="todas as notificações"
        requireTypedConfirmation={false}
        onConfirm={onConfirmClearAll}
        isPending={isClearAllPending}
      />
    </>
  );
};
