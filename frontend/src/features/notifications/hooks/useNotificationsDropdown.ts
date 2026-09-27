import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
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
import { resolveEntityUrl } from "../utils";

const ITEMS_PER_PAGE = 10;

/**
 * Smart Hook para gerenciamento do dropdown de notificações.
 * Encapsula chamadas de API (Orval/React Query), paginação, modo de seleção múltipla
 * e diálogos de confirmação de exclusão.
 */
export function useNotificationsDropdown() {
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

  const handleToggleSelectionMode = () => {
    setIsSelectionMode((prev) => !prev);
    setSelectedIds(new Set());
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

  const handleOpenClearAllDialog = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (rawNotifications.length > 0) {
      setIsClearAllDialogOpen(true);
    }
  };

  const handleConfirmClearAll = () => {
    clearAll.mutate();
  };

  return {
    page,
    setPage,
    totalPages,
    totalCount,
    unreadCount,
    notifications: rawNotifications,
    isLoading,
    isSelectionMode,
    selectedIds,
    isClearAllDialogOpen,
    setIsClearAllDialogOpen,
    isMarkAllPending: markAllAsRead.isPending,
    isBulkMarkAsReadPending: bulkMarkAsRead.isPending,
    isBulkDeletePending: bulkDelete.isPending,
    isClearAllPending: clearAll.isPending,
    handleSelectNotification,
    handleMarkAsReadSingle,
    handleDeleteSingle,
    handleMarkAllAsRead,
    handleToggleSelectionMode,
    toggleSelectNotification,
    handleToggleSelectAll,
    handleBulkMarkAsRead,
    handleBulkDelete,
    handleOpenClearAllDialog,
    handleConfirmClearAll,
  };
}
