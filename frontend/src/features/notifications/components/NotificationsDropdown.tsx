import React from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCheck, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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

export const NotificationsDropdown: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: notificationsResponse, isLoading } = useNotificationsList();
  const notifications = notificationsResponse?.data ?? [];

  const { data: unreadResponse } = useNotificationsUnreadCount();
  const unreadCount = unreadResponse?.data?.count ?? 0;

  const markAsRead = useNotificationsMarkAsRead({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getNotificationsListQueryKey() });
        queryClient.invalidateQueries({ queryKey: getNotificationsUnreadCountQueryKey() });
      },
    },
  });

  const markAllAsRead = useNotificationsMarkAllAsRead({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getNotificationsListQueryKey() });
        queryClient.invalidateQueries({ queryKey: getNotificationsUnreadCountQueryKey() });
      },
    },
  });

  const handleSelectNotification = (notification: NotificationOut) => {
    if (!notification.is_read) {
      markAsRead.mutate({ notificationId: notification.uuid });
    }
    const targetRoute = resolveNotificationRoute(notification.link);
    navigate(targetRoute);
  };

  const handleMarkAllAsRead = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    markAllAsRead.mutate();
  };

  return (
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

      <DropdownMenuContent align="end" className="w-80 sm:w-96 p-0 max-h-[85vh] flex flex-col">
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <DropdownMenuLabel className="p-0 font-semibold text-sm">
            Notificações
          </DropdownMenuLabel>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleMarkAllAsRead}
              disabled={markAllAsRead.isPending}
              className="h-auto p-0 text-xs text-primary hover:text-primary/80 font-normal cursor-pointer"
            >
              <CheckCheck className="size-3.5 mr-1 inline-block" />
              Marcar todas como lidas
            </Button>
          )}
        </div>

        <div className="overflow-y-auto max-h-96 p-2 flex flex-col gap-1">
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
                  onSelect={handleSelectNotification}
                />
              </DropdownMenuItem>
            ))
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
