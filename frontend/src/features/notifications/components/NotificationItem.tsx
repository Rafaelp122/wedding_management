import type { NotificationOut } from "@/api/generated/v1/models";
import { formatDateTimeBR } from "@/lib/formatters";
import { cn } from "@/lib/utils";
import { AlertTriangle, Bell, Clock, FileText } from "lucide-react";
import React from "react";

export interface NotificationItemProps extends React.HTMLAttributes<HTMLDivElement> {
  notification: NotificationOut;
  onSelect?: (notification: NotificationOut) => void;
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
  ({ notification, onSelect, className, onClick, onKeyDown, asChild, ...props }: NotificationItemProps & { asChild?: boolean }, ref) => {
    const IconComponent = getNotificationIcon(notification.type);

    const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
      onClick?.(e);
      onSelect?.(notification);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
      onKeyDown?.(e);
      if ((e.key === "Enter" || e.key === " ") && !e.defaultPrevented) {
        onSelect?.(notification);
      }
    };

    return (
      <div
        ref={ref}
        role="button"
        tabIndex={0}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        className={cn(
          "flex items-start gap-3 p-3 text-left rounded-lg transition-colors cursor-pointer select-none w-full",
          "hover:bg-accent hover:text-accent-foreground",
          !notification.is_read && "bg-muted/40 font-medium",
          className
        )}
        {...props}
      >
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
            <p className="text-sm font-semibold truncate text-foreground">
              {notification.title}
            </p>
            {!notification.is_read && (
              <span
                data-testid="unread-indicator"
                className="size-2 rounded-full bg-destructive shrink-0"
                title="Não lida"
              />
            )}
          </div>
          <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
            {notification.message}
          </p>
          <span className="text-[10px] text-muted-foreground/80 mt-1 block">
            {formatDateTimeBR(notification.created_at)}
          </span>
        </div>
      </div>
    );
  }
);

NotificationItem.displayName = "NotificationItem";
