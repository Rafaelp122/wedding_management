import React from "react";
import { useNotificationsDropdown } from "../hooks/useNotificationsDropdown";
import { NotificationsDropdownView } from "./NotificationsDropdownView";

export { resolveNotificationRoute, resolveEntityUrl } from "../utils";

/**
 * Componente Container (Smart Component) de Notificações.
 * Orquestra o hook `useNotificationsDropdown` com o presenter `NotificationsDropdownView`.
 */
export const NotificationsDropdown: React.FC = () => {
  const dropdown = useNotificationsDropdown();

  return (
    <NotificationsDropdownView
      page={dropdown.page}
      totalPages={dropdown.totalPages}
      totalCount={dropdown.totalCount}
      unreadCount={dropdown.unreadCount}
      notifications={dropdown.notifications}
      isLoading={dropdown.isLoading}
      isSelectionMode={dropdown.isSelectionMode}
      selectedIds={dropdown.selectedIds}
      isClearAllDialogOpen={dropdown.isClearAllDialogOpen}
      isMarkAllPending={dropdown.isMarkAllPending}
      isBulkMarkAsReadPending={dropdown.isBulkMarkAsReadPending}
      isBulkDeletePending={dropdown.isBulkDeletePending}
      isClearAllPending={dropdown.isClearAllPending}
      onPageChange={dropdown.setPage}
      onOpenClearAllDialogChange={dropdown.setIsClearAllDialogOpen}
      onSelectNotification={dropdown.handleSelectNotification}
      onMarkAsReadSingle={dropdown.handleMarkAsReadSingle}
      onDeleteSingle={dropdown.handleDeleteSingle}
      onMarkAllAsRead={dropdown.handleMarkAllAsRead}
      onToggleSelectionMode={dropdown.handleToggleSelectionMode}
      onToggleSelectNotification={dropdown.toggleSelectNotification}
      onToggleSelectAll={dropdown.handleToggleSelectAll}
      onBulkMarkAsRead={dropdown.handleBulkMarkAsRead}
      onBulkDelete={dropdown.handleBulkDelete}
      onOpenClearAllDialog={dropdown.handleOpenClearAllDialog}
      onConfirmClearAll={dropdown.handleConfirmClearAll}
    />
  );
};
