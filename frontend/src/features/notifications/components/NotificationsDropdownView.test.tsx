import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { NotificationsDropdownView } from "./NotificationsDropdownView";
import type { NotificationOut } from "@/api/generated/v1/models";

const mockNotification: NotificationOut = {
  uuid: "notif-1",
  title: "Pagamento Pendente",
  message: "A parcela 2 vence amanhã",
  type: "UPCOMING_INSTALLMENT",
  is_read: false,
  link: "/finances",
  created_at: "2026-08-08T12:00:00Z",
};

describe("NotificationsDropdownView", () => {
  const defaultProps = {
    page: 1,
    totalPages: 1,
    totalCount: 1,
    unreadCount: 1,
    notifications: [mockNotification],
    isLoading: false,
    isSelectionMode: false,
    selectedIds: new Set<string>(),
    isClearAllDialogOpen: false,
    onPageChange: vi.fn(),
    onOpenClearAllDialogChange: vi.fn(),
    onSelectNotification: vi.fn(),
    onMarkAsReadSingle: vi.fn(),
    onDeleteSingle: vi.fn(),
    onMarkAllAsRead: vi.fn(),
    onToggleSelectionMode: vi.fn(),
    onToggleSelectNotification: vi.fn(),
    onToggleSelectAll: vi.fn(),
    onBulkMarkAsRead: vi.fn(),
    onBulkDelete: vi.fn(),
    onOpenClearAllDialog: vi.fn(),
    onConfirmClearAll: vi.fn(),
  };

  it("renders trigger button and badge with unread count", () => {
    render(<NotificationsDropdownView {...defaultProps} unreadCount={5} />);
    expect(screen.getByRole("button", { name: "Notificações" })).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("renders empty state when there are no notifications", async () => {
    const user = userEvent.setup();
    render(
      <NotificationsDropdownView
        {...defaultProps}
        notifications={[]}
        totalCount={0}
        unreadCount={0}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Notificações" }));
    expect(
      screen.getByText("Você não tem novas notificações no momento."),
    ).toBeInTheDocument();
  });

  it("renders notification item and calls onSelectNotification on click", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(
      <NotificationsDropdownView
        {...defaultProps}
        onSelectNotification={onSelect}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Notificações" }));
    expect(screen.getByText("Pagamento Pendente")).toBeInTheDocument();

    await user.click(screen.getByText("Pagamento Pendente"));
    expect(onSelect).toHaveBeenCalledWith(mockNotification);
  });

  it("calls onMarkAllAsRead when clicking mark all button", async () => {
    const user = userEvent.setup();
    const onMarkAll = vi.fn();
    render(
      <NotificationsDropdownView
        {...defaultProps}
        onMarkAllAsRead={onMarkAll}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Notificações" }));
    await user.click(screen.getByText("Marcar todas como lidas"));

    expect(onMarkAll).toHaveBeenCalled();
  });

  it("toggles selection mode and calls onToggleSelectionMode", async () => {
    const user = userEvent.setup();
    const onToggle = vi.fn();
    render(
      <NotificationsDropdownView
        {...defaultProps}
        onToggleSelectionMode={onToggle}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Notificações" }));
    await user.click(screen.getByText("Selecionar"));

    expect(onToggle).toHaveBeenCalled();
  });

  it("renders selection toolbar and handles bulk actions", async () => {
    const user = userEvent.setup();
    const onBulkMarkAsRead = vi.fn();
    const onBulkDelete = vi.fn();

    render(
      <NotificationsDropdownView
        {...defaultProps}
        isSelectionMode={true}
        selectedIds={new Set(["notif-1"])}
        onBulkMarkAsRead={onBulkMarkAsRead}
        onBulkDelete={onBulkDelete}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Notificações" }));
    expect(screen.getByText("1 selecionada(s)")).toBeInTheDocument();

    await user.click(screen.getByText("Lidas"));
    expect(onBulkMarkAsRead).toHaveBeenCalled();

    await user.click(screen.getByText("Excluir"));
    expect(onBulkDelete).toHaveBeenCalled();
  });

  it("renders pagination and calls onPageChange", async () => {
    const user = userEvent.setup();
    const onPageChange = vi.fn();

    render(
      <NotificationsDropdownView
        {...defaultProps}
        page={1}
        totalPages={3}
        onPageChange={onPageChange}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Notificações" }));
    expect(screen.getByText("Página 1 de 3")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /próxima/i }));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });
});
