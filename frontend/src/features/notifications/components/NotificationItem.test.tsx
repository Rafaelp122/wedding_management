import { render, screen, userEvent } from "@/test-utils";
import { describe, expect, it, vi } from "vitest";
import type { NotificationOut } from "@/api/generated/v1/models";
import { NotificationItem } from "./NotificationItem";

const mockNotification: NotificationOut = {
  uuid: "notif-123",
  title: "Parcela Vencida",
  message: "A parcela do buffet venceu ontem.",
  type: "OVERDUE_INSTALLMENT",
  wedding_name: "Casamento de Ana e Pedro",
  is_read: false,
  link: "/finances",
  created_at: "2026-08-08T10:00:00Z",
};

describe("NotificationItem", () => {
  it("renders notification title, message, wedding_name badge, and formatted date", () => {
    render(
      <NotificationItem notification={mockNotification} onSelect={vi.fn()} />
    );

    expect(screen.getByText("Parcela Vencida")).toBeInTheDocument();
    expect(
      screen.getByText("A parcela do buffet venceu ontem.")
    ).toBeInTheDocument();
    expect(screen.getByText("Casamento de Ana e Pedro")).toBeInTheDocument();
    expect(screen.getByText("Ver detalhes")).toBeInTheDocument();
  });

  it("renders affordance and disabled check icon when notification is read", () => {
    render(
      <NotificationItem
        notification={{ ...mockNotification, is_read: true }}
        onSelect={vi.fn()}
        onMarkAsRead={vi.fn()}
      />
    );

    expect(screen.queryByTestId("unread-indicator")).not.toBeInTheDocument();
    expect(screen.getByText("Ver detalhes")).toBeInTheDocument();
    const disabledCheckBtn = screen.getByTitle("Esta notificação já foi marcada como lida");
    expect(disabledCheckBtn).toBeDisabled();
  });

  it("calls onSelect when clicked", async () => {
    const handleSelect = vi.fn();
    const user = userEvent.setup();

    render(
      <NotificationItem
        notification={mockNotification}
        onSelect={handleSelect}
      />
    );

    await user.click(screen.getByRole("button"));
    expect(handleSelect).toHaveBeenCalledWith(mockNotification);
  });

  it("calls onMarkAsRead when check action button is clicked without calling onSelect", async () => {
    const handleSelect = vi.fn();
    const handleMarkAsRead = vi.fn();
    const user = userEvent.setup();

    render(
      <NotificationItem
        notification={mockNotification}
        onSelect={handleSelect}
        onMarkAsRead={handleMarkAsRead}
      />
    );

    const markBtn = screen.getByTitle("Marcar como lida");
    await user.click(markBtn);

    expect(handleMarkAsRead).toHaveBeenCalledWith(mockNotification);
    expect(handleSelect).not.toHaveBeenCalled();
  });

  it("calls onDelete when trash action button is clicked without calling onSelect", async () => {
    const handleSelect = vi.fn();
    const handleDelete = vi.fn();
    const user = userEvent.setup();

    render(
      <NotificationItem
        notification={mockNotification}
        onSelect={handleSelect}
        onDelete={handleDelete}
      />
    );

    const deleteBtn = screen.getByTitle("Apagar notificação");
    await user.click(deleteBtn);

    expect(handleDelete).toHaveBeenCalledWith(mockNotification);
    expect(handleSelect).not.toHaveBeenCalled();
  });

  it("renders correct icons for different notification types", () => {
    const types = [
      "OVERDUE_INSTALLMENT",
      "CHECKLIST_ITEM_OVERDUE",
      "UPCOMING_INSTALLMENT",
      "TASK_DEADLINE",
      "EXPIRING_CONTRACT",
      "GENERAL",
    ];

    types.forEach((type) => {
      const { container, unmount } = render(
        <NotificationItem
          notification={{ ...mockNotification, type }}
          onSelect={vi.fn()}
        />
      );
      expect(container.querySelector("svg")).toBeInTheDocument();
      unmount();
    });
  });

  it("calls onSelect when Enter or Space key is pressed", async () => {
    const handleSelect = vi.fn();
    const user = userEvent.setup();

    render(
      <NotificationItem
        notification={mockNotification}
        onSelect={handleSelect}
      />
    );

    const button = screen.getByRole("button");
    button.focus();
    await user.keyboard("{Enter}");
    expect(handleSelect).toHaveBeenCalledTimes(1);

    await user.keyboard(" ");
    expect(handleSelect).toHaveBeenCalledTimes(2);
  });

  it("renders checkbox and calls onToggleSelect in selectable mode", async () => {
    const handleToggleSelect = vi.fn();
    const user = userEvent.setup();

    render(
      <NotificationItem
        notification={mockNotification}
        selectable={true}
        selected={false}
        onToggleSelect={handleToggleSelect}
      />
    );

    const checkbox = screen.getByLabelText(`Selecionar notificação ${mockNotification.title}`);
    expect(checkbox).toBeInTheDocument();

    await user.click(checkbox);
    expect(handleToggleSelect).toHaveBeenCalledWith(mockNotification);

    await user.click(screen.getByRole("button"));
    expect(handleToggleSelect).toHaveBeenCalledTimes(2);
  });
});
