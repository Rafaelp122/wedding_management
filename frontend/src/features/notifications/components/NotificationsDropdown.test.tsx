import { render, screen, userEvent, waitFor, server } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import { NotificationsDropdown, resolveEntityUrl } from "./NotificationsDropdown";
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

describe("resolveEntityUrl", () => {
  it("resolves expense target route with wedding_id and target_id", () => {
    const notification: NotificationOut = {
      uuid: "1",
      title: "Test",
      message: "Test",
      type: "EXPENSE",
      target_type: "expense",
      target_id: "exp-123",
      wedding_id: "wed-456",
      is_read: false,
      link: "",
      created_at: "2026-08-08T12:00:00Z",
    };
    expect(resolveEntityUrl(notification)).toBe(
      "/weddings/wed-456?tab=finances&expense_id=exp-123",
    );
  });

  it("resolves installment target route with wedding_id and target_id", () => {
    const notification: NotificationOut = {
      uuid: "1",
      title: "Test",
      message: "Test",
      type: "INSTALLMENT",
      target_type: "installment",
      target_id: "inst-123",
      wedding_id: "wed-456",
      is_read: false,
      link: "",
      created_at: "2026-08-08T12:00:00Z",
    };
    expect(resolveEntityUrl(notification)).toBe(
      "/weddings/wed-456?tab=finances&expense_id=inst-123",
    );
  });

  it("resolves expense target route without target_id", () => {
    const notification: NotificationOut = {
      uuid: "1",
      title: "Test",
      message: "Test",
      type: "EXPENSE",
      target_type: "expense",
      target_id: null,
      wedding_id: "wed-456",
      is_read: false,
      link: "",
      created_at: "2026-08-08T12:00:00Z",
    };
    expect(resolveEntityUrl(notification)).toBe("/weddings/wed-456?tab=finances");
  });

  it("resolves task target route with wedding_id and target_id", () => {
    const notification: NotificationOut = {
      uuid: "1",
      title: "Test",
      message: "Test",
      type: "TASK",
      target_type: "task",
      target_id: "task-789",
      wedding_id: "wed-456",
      is_read: false,
      link: "",
      created_at: "2026-08-08T12:00:00Z",
    };
    expect(resolveEntityUrl(notification)).toBe(
      "/weddings/wed-456?tab=planning&subtab=checklist&task_id=task-789",
    );
  });

  it("resolves contract target route with wedding_id and target_id", () => {
    const notification: NotificationOut = {
      uuid: "1",
      title: "Test",
      message: "Test",
      type: "CONTRACT",
      target_type: "contract",
      target_id: "contract-101",
      wedding_id: "wed-456",
      is_read: false,
      link: "",
      created_at: "2026-08-08T12:00:00Z",
    };
    expect(resolveEntityUrl(notification)).toBe(
      "/weddings/wed-456?tab=logistics&contract_id=contract-101",
    );
  });

  it("resolves wedding target route with wedding_id", () => {
    const notification: NotificationOut = {
      uuid: "1",
      title: "Test",
      message: "Test",
      type: "WEDDING",
      target_type: "wedding",
      target_id: null,
      wedding_id: "wed-456",
      is_read: false,
      link: "",
      created_at: "2026-08-08T12:00:00Z",
    };
    expect(resolveEntityUrl(notification)).toBe("/weddings/wed-456");
  });

  it("falls back to link when wedding_id is missing", () => {
    const notification: NotificationOut = {
      uuid: "1",
      title: "Test",
      message: "Test",
      type: "GENERAL",
      target_type: undefined,
      target_id: null,
      wedding_id: null,
      is_read: false,
      link: "/suppliers",
      created_at: "2026-08-08T12:00:00Z",
    };
    expect(resolveEntityUrl(notification)).toBe("/suppliers");
  });

  it("falls back to /dashboard when wedding_id and link are missing", () => {
    const notification: NotificationOut = {
      uuid: "1",
      title: "Test",
      message: "Test",
      type: "GENERAL",
      target_type: undefined,
      target_id: null,
      wedding_id: null,
      is_read: false,
      link: "",
      created_at: "2026-08-08T12:00:00Z",
    };
    expect(resolveEntityUrl(notification)).toBe("/dashboard");
  });
});

describe("NotificationsDropdown", () => {
  it("renders trigger button and unread count badge", async () => {
    server.use(
      getNotificationsUnreadCountMockHandler({ count: 3 }),
      getNotificationsListMockHandler({ items: mockNotifications, count: mockNotifications.length })
    );

    render(<NotificationsDropdown />);

    expect(screen.getByRole("button", { name: "Notificações" })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("3")).toBeInTheDocument();
    });
  });

  it("opens menu and displays list of notifications", async () => {
    server.use(
      getNotificationsUnreadCountMockHandler({ count: 1 }),
      getNotificationsListMockHandler({ items: mockNotifications, count: mockNotifications.length })
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    const trigger = screen.getByRole("button", { name: "Notificações" });
    await user.click(trigger);

    await waitFor(() => {
      expect(screen.getByText("Pagamento Pendente")).toBeInTheDocument();
      expect(screen.getByText("Contrato Próximo do Fim")).toBeInTheDocument();
    });
  });

  it("renders empty state message when there are no notifications", async () => {
    server.use(
      getNotificationsUnreadCountMockHandler({ count: 0 }),
      getNotificationsListMockHandler({ items: [], count: 0 })
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    const trigger = screen.getByRole("button", { name: "Notificações" });
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
      getNotificationsListMockHandler({ items: mockNotifications, count: mockNotifications.length }),
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

    const trigger = screen.getByRole("button", { name: "Notificações" });
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
      getNotificationsListMockHandler({ items: mockNotifications, count: mockNotifications.length }),
      getNotificationsMarkAllAsReadMockHandler(() => {
        markAllSpy();
        return { marked_count: 2 };
      })
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    const trigger = screen.getByRole("button", { name: "Notificações" });
    await user.click(trigger);

    await waitFor(() => {
      expect(screen.getByText("Marcar todas como lidas")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Marcar todas como lidas"));

    await waitFor(() => {
      expect(markAllSpy).toHaveBeenCalled();
    });
  });

  it("disables mark all and clear all header buttons with tooltips when unreadCount is 0 or list is empty", async () => {
    server.use(
      getNotificationsUnreadCountMockHandler({ count: 0 }),
      getNotificationsListMockHandler({ items: [], count: 0 })
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    const trigger = screen.getByRole("button", { name: "Notificações" });
    await user.click(trigger);

    await waitFor(() => {
      const markAllBtn = screen.getByTitle("Não há notificações pendentes para leitura");
      const clearAllBtn = screen.getByTitle("Não há notificações para apagar");

      expect(markAllBtn).toBeDisabled();
      expect(clearAllBtn).toBeDisabled();
    });
  });

  it("handles selection mode, toggling select all, and bulk operations", async () => {
    const bulkMarkSpy = vi.fn();
    const bulkDeleteSpy = vi.fn();

    server.use(
      getNotificationsUnreadCountMockHandler({ count: 2 }),
      getNotificationsListMockHandler({ items: mockNotifications, count: mockNotifications.length }),
      http.post("*/api/v1/notifications/bulk-read/", async () => {
        bulkMarkSpy();
        return HttpResponse.json({ affected_count: 2 });
      }),
      http.post("*/api/v1/notifications/bulk-delete/", async () => {
        bulkDeleteSpy();
        return HttpResponse.json({ affected_count: 2 });
      })
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    await user.click(screen.getByRole("button", { name: "Notificações" }));
    await waitFor(() => expect(screen.getByText("Selecionar")).toBeInTheDocument());

    await user.click(screen.getByText("Selecionar"));
    expect(screen.getByText("Selecionar todas")).toBeInTheDocument();

    const selectAllCheckbox = screen.getByLabelText("Selecionar todas as notificações");
    await user.click(selectAllCheckbox);
    expect(screen.getByText("2 selecionada(s)")).toBeInTheDocument();

    await user.click(screen.getByText("Lidas"));
    await waitFor(() => expect(bulkMarkSpy).toHaveBeenCalled());

    await user.click(selectAllCheckbox);
    await user.click(screen.getByText("Excluir"));
    await waitFor(() => expect(bulkDeleteSpy).toHaveBeenCalled());
  });

  it("handles single notification delete action", async () => {
    const deleteSpy = vi.fn();

    server.use(
      getNotificationsUnreadCountMockHandler({ count: 1 }),
      getNotificationsListMockHandler({ items: mockNotifications, count: mockNotifications.length }),
      http.delete("*/api/v1/notifications/:id/", () => {
        deleteSpy();
        return new HttpResponse(null, { status: 204 });
      })
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    await user.click(screen.getByRole("button", { name: "Notificações" }));
    await waitFor(() => expect(screen.getByText("Pagamento Pendente")).toBeInTheDocument());

    const deleteBtns = screen.getAllByTitle("Apagar notificação");
    await user.click(deleteBtns[0]);
    await waitFor(() => expect(deleteSpy).toHaveBeenCalled());
  });

  it("opens clear all dialog and calls clearAll mutation on confirm", async () => {
    const clearAllSpy = vi.fn();

    server.use(
      getNotificationsUnreadCountMockHandler({ count: 1 }),
      getNotificationsListMockHandler({ items: mockNotifications, count: mockNotifications.length }),
      http.delete("*/api/v1/notifications/clear-all/", () => {
        clearAllSpy();
        return HttpResponse.json({ affected_count: 2 });
      })
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    await user.click(screen.getByRole("button", { name: "Notificações" }));
    await waitFor(() => expect(screen.getByTitle("Apagar todas as notificações")).toBeInTheDocument());

    await user.click(screen.getByTitle("Apagar todas as notificações"));
    expect(await screen.findByText("Apagar todas as notificações?")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /deletar/i }));
    await waitFor(() => expect(clearAllSpy).toHaveBeenCalled());
  });

  it("renders pagination controls when total count exceeds items per page", async () => {
    const pagedItems = Array.from({ length: 15 }, (_, i) => ({
      ...mockNotifications[0],
      uuid: `notif-page-${i}`,
      title: `Notificação Pagina ${i + 1}`,
    }));

    server.use(
      getNotificationsUnreadCountMockHandler({ count: 15 }),
      getNotificationsListMockHandler({ items: pagedItems.slice(0, 10), count: 15 })
    );

    const user = userEvent.setup();
    render(<NotificationsDropdown />);

    await user.click(screen.getByRole("button", { name: "Notificações" }));
    await waitFor(() => expect(screen.getByText("Página 1 de 2")).toBeInTheDocument());

    const nextBtn = screen.getByRole("button", { name: /próxima/i });
    expect(nextBtn).not.toBeDisabled();
    await user.click(nextBtn);

    const prevBtn = screen.getByRole("button", { name: /anterior/i });
    expect(prevBtn).toBeInTheDocument();
  });
});
