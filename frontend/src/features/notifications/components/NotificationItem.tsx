import type { NotificationOut } from "@/api/generated/v1/models";
import { Checkbox } from "@/components/ui/checkbox";
import { formatDateTimeBR } from "@/lib/formatters";
import { cn } from "@/lib/utils";
import { AlertTriangle, Bell, Check, ChevronRight, Clock, FileText, Heart, Trash2 } from "lucide-react";
import React from "react";

export interface NotificationItemProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "onSelect"> {
  notification: NotificationOut;
  onSelect?: (notification: NotificationOut) => void;
  onMarkAsRead?: (notification: NotificationOut) => void;
  onDelete?: (notification: NotificationOut) => void;
  selectable?: boolean;
  selected?: boolean;
  onToggleSelect?: (notification: NotificationOut) => void;
}

export const getNotificationIcon = (type: string) => {
  switch (type) {
    case "OVERDUE_INSTALLMENT":
    case "CHECKLIST_ITEM_OVERDUE":
      return AlertTriangle;
    case "UPCOMING_INSTALLMENT":
    case "TASK_DEADLINE":
      return Clock;
    case "EXPIRING_CONTRACT":
      return FileText;
    case "GENERAL":
    default:
      return Bell;
  }
};

export const NotificationItem = React.forwardRef<HTMLDivElement, NotificationItemProps>(
  (
    {
      notification,
      onSelect,
      onMarkAsRead,
      onDelete,
      selectable = false,
      selected = false,
      onToggleSelect,
      className,
      onClick,
      onKeyDown,
      _asChild,
      ...props
    }: NotificationItemProps & { _asChild?: boolean },
    ref
  ) => {
    const IconComponent = getNotificationIcon(notification.type);

    const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
      onClick?.(e);
      if (selectable) {
        onToggleSelect?.(notification);
      } else {
        onSelect?.(notification);
      }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
      onKeyDown?.(e);
      if ((e.key === "Enter" || e.key === " ") && !e.defaultPrevented) {
        if (selectable) {
          onToggleSelect?.(notification);
        } else {
          onSelect?.(notification);
        }
      }
    };

    const handleMarkAsReadClick = (e: React.MouseEvent) => {
      e.stopPropagation();
      onMarkAsRead?.(notification);
    };

    const handleDeleteClick = (e: React.MouseEvent) => {
      e.stopPropagation();
      onDelete?.(notification);
    };

    return (
      <div
        ref={ref}
        role="button"
        tabIndex={0}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        className={cn(
          "group relative flex items-start gap-3 p-3 text-left rounded-lg transition-all cursor-pointer select-none w-full border",
          "hover:bg-accent/60 hover:text-accent-foreground",
          !notification.is_read
            ? "bg-muted/40 font-medium border-l-4 border-l-primary border-border"
            : "bg-background border-border/50 text-muted-foreground",
          selected && "bg-primary/5 border-primary/40",
          className
        )}
        {...props}
      >
        {selectable && (
          <div
            className="flex items-center justify-center pt-1"
            onClick={(e) => e.stopPropagation()}
          >
            <Checkbox
              checked={selected}
              onCheckedChange={() => onToggleSelect?.(notification)}
              aria-label={`Selecionar notificação ${notification.title}`}
            />
          </div>
        )}

        <div
          className={cn(
            "p-2 rounded-full shrink-0 mt-0.5",
            notification.type === "OVERDUE_INSTALLMENT" ||
              notification.type === "CHECKLIST_ITEM_OVERDUE"
              ? "bg-destructive/10 text-destructive"
              : notification.type === "UPCOMING_INSTALLMENT" ||
                notification.type === "TASK_DEADLINE"
              ? "bg-amber-500/10 text-amber-600 dark:text-amber-400"
              : notification.type === "EXPIRING_CONTRACT"
              ? "bg-blue-500/10 text-blue-600 dark:text-blue-400"
              : "bg-primary/10 text-primary"
          )}
        >
          <IconComponent className="size-4 shrink-0" aria-hidden="true" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-semibold truncate text-foreground pr-1">
              {notification.title}
            </p>

            <div className="flex items-center gap-1 shrink-0">
              {!notification.is_read && onMarkAsRead && (
                <button
                  type="button"
                  onClick={handleMarkAsReadClick}
                  title="Marcar como lida"
                  aria-label="Marcar notificação como lida"
                  className="p-1 rounded-md text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors"
                >
                  <Check className="size-3.5" />
                </button>
              )}

              {onDelete && (
                <button
                  type="button"
                  onClick={handleDeleteClick}
                  title="Apagar notificação"
                  aria-label="Apagar notificação"
                  className="p-1 rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                >
                  <Trash2 className="size-3.5" />
                </button>
              )}

              {!notification.is_read && !onMarkAsRead && (
                <span
                  data-testid="unread-indicator"
                  className="size-2 rounded-full bg-primary shrink-0"
                  title="Não lida"
                />
              )}
            </div>
          </div>

          <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
            {notification.message}
          </p>

          {notification.wedding_name && (
            <div className="mt-1">
              <span className="inline-flex items-center gap-1 text-[11px] font-medium text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/50 px-2 py-0.5 rounded-full">
                <Heart className="size-3 text-rose-500 fill-rose-500/20" aria-hidden="true" />
                {notification.wedding_name}
              </span>
            </div>
          )}

          <div className="flex items-center justify-between mt-1.5 pt-0.5">
            <span className="text-[10px] text-muted-foreground/80">
              {formatDateTimeBR(notification.created_at)}
            </span>

            {Boolean(notification.link) && !selectable && (
              <div className="flex items-center gap-0.5 text-[11px] font-medium text-primary group-hover:underline">
                <span>Ver detalhes</span>
                <ChevronRight className="size-3 transition-transform group-hover:translate-x-0.5" />
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
);

NotificationItem.displayName = "NotificationItem";
