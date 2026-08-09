import { render, screen, userEvent } from "@/test-utils";
import { describe, expect, it, vi } from "vitest";
import type { NotificationOut } from "@/api/generated/v1/models";
import { NotificationItem } from "./NotificationItem";

const mockNotification: NotificationOut = {
  uuid: "notif-123",
  title: "Parcela Vencida",
  message: "A parcela do buffet venceu ontem.",
  type: "OVERDUE_INSTALLMENT",
  is_read: false,
  link: "/finances",
  created_at: "2026-08-08T10:00:00Z",
};

describe("NotificationItem", () => {
  it("renders notification title, message, and formatted date", () => {
    render(
      <NotificationItem notification={mockNotification} onSelect={vi.fn()} />
    );

    expect(screen.getByText("Parcela Vencida")).toBeInTheDocument();
    expect(
      screen.getByText("A parcela do buffet venceu ontem.")
    ).toBeInTheDocument();
    expect(screen.getByTestId("unread-indicator")).toBeInTheDocument();
  });

  it("does not render unread indicator when is_read is true", () => {
    render(
      <NotificationItem
        notification={{ ...mockNotification, is_read: true }}
        onSelect={vi.fn()}
      />
    );

    expect(screen.queryByTestId("unread-indicator")).not.toBeInTheDocument();
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
});
