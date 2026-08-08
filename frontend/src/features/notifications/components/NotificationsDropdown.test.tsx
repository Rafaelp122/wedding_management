import { render, screen, userEvent, waitFor, server } from "@/test-utils";
import { describe, expect, it, vi } from "vitest";
import { NotificationsDropdown } from "./NotificationsDropdown";
import {
  getNotificationsListMockHandler,
  getNotificationsUnreadCountMockHandler,
  getNotificationsMarkAsReadMockHandler,
  getNotificationsMarkAllAsReadMockHandler,
} from "@/api/generated/v1/endpoints/notifications/notifications.msw";
import type { NotificationOut } from "@/api/generated/v1/models";

const mockNotifications: NotificationOut[] = [
  {
    uuid: "notif-1",
    title: "Pagamento Pendente",
    message: "A parcela 2 do fotógrafo vence em breve",
    type: "UPCOMING_INSTALLMENT",
    is_read: false,
    link: "/finances/expenses",
    created_at: "2026-08-08T12:00:00Z",
  },
  {
    uuid: "notif-2",
    title: "Contrato Próximo do Fim",
    message: "O contrato com a florista expira em 5 dias",
    type: "EXPIRING_CONTRACT",
    is_read: true,
    link: "/logistics/contracts",
    created_at: "2026-08-07T08:30:00Z",
  },
];

describe("NotificationsDropdown", () => {
  it("renders trigger button and unread count badge", async () => {
    server.use(
      getNotificationsUnreadCountMockHandler({ count: 3 }),
      getNotificationsListMockHandler(mockNotifications)
    );

    render(<NotificationsDropdown />);

    expect(screen.getByRole("button", { name: /notificações/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("3")).toBeInTheDocument();
    });
  });

  it("opens menu and displays list of notifications", async () => {
    server.use(
      getNotificationsUnreadCountMockHandler({ count: 1 }),
      getNotificationsListMockHandler(mockNotifications)
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    const trigger = screen.getByRole("button", { name: /notificações/i });
    await user.click(trigger);

    await waitFor(() => {
      expect(screen.getByText("Pagamento Pendente")).toBeInTheDocument();
      expect(screen.getByText("Contrato Próximo do Fim")).toBeInTheDocument();
    });
  });

  it("renders empty state message when there are no notifications", async () => {
    server.use(
      getNotificationsUnreadCountMockHandler({ count: 0 }),
      getNotificationsListMockHandler([])
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    const trigger = screen.getByRole("button", { name: /notificações/i });
    await user.click(trigger);

    await waitFor(() => {
      expect(
        screen.getByText("Você não tem novas notificações no momento.")
      ).toBeInTheDocument();
    });
  });

  it("marks item as read when selected", async () => {
    const markAsReadSpy = vi.fn();

    server.use(
      getNotificationsUnreadCountMockHandler({ count: 1 }),
      getNotificationsListMockHandler(mockNotifications),
      getNotificationsMarkAsReadMockHandler((info) => {
        markAsReadSpy(info.params.notificationId);
        return {
          ...mockNotifications[0],
          is_read: true,
        };
      })
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    const trigger = screen.getByRole("button", { name: /notificações/i });
    await user.click(trigger);

    await waitFor(() => {
      expect(screen.getByText("Pagamento Pendente")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Pagamento Pendente"));

    await waitFor(() => {
      expect(markAsReadSpy).toHaveBeenCalledWith("notif-1");
    });
  });

  it("marks all notifications as read when header action is clicked", async () => {
    const markAllSpy = vi.fn();

    server.use(
      getNotificationsUnreadCountMockHandler({ count: 2 }),
      getNotificationsListMockHandler(mockNotifications),
      getNotificationsMarkAllAsReadMockHandler(() => {
        markAllSpy();
        return { marked_count: 2 };
      })
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    const trigger = screen.getByRole("button", { name: /notificações/i });
    await user.click(trigger);

    await waitFor(() => {
      expect(screen.getByText("Marcar todas como lidas")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Marcar todas como lidas"));

    await waitFor(() => {
      expect(markAllSpy).toHaveBeenCalled();
    });
  });
});
