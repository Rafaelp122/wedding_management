import { describe, expect, it, vi } from "vitest";
import type { AxiosRequestHeaders } from "axios";
import { createQueue } from "@/api/utils/queue-manager";
import type { FailedQueueItem } from "@/api/types/queue";

function createQueueItem(overrides: Partial<FailedQueueItem> = {}): FailedQueueItem {
  return {
    resolve: vi.fn(),
    reject: vi.fn(),
    config: { headers: {} as unknown as AxiosRequestHeaders },
    ...overrides,
  } as FailedQueueItem;
}

describe("createQueue", () => {
  describe("process", () => {
    it("resolves all queued items with token", () => {
      const queue = createQueue();
      const item1 = createQueueItem();
      const item2 = createQueueItem();

      queue.enqueue(item1);
      queue.enqueue(item2);
      queue.process(null, "new-token");

      expect(item1.resolve).toHaveBeenCalledWith("new-token");
      expect(item2.resolve).toHaveBeenCalledWith("new-token");
      expect(item1.reject).not.toHaveBeenCalled();
      expect(item2.reject).not.toHaveBeenCalled();
    });

    it("rejects all queued items with error", () => {
      const queue = createQueue();
      const item1 = createQueueItem();
      const item2 = createQueueItem();
      const err = new Error("refresh failed");

      queue.enqueue(item1);
      queue.enqueue(item2);
      queue.process(err, null);

      expect(item1.reject).toHaveBeenCalledWith(err);
      expect(item2.reject).toHaveBeenCalledWith(err);
      expect(item1.resolve).not.toHaveBeenCalled();
      expect(item2.resolve).not.toHaveBeenCalled();
    });

    it("rejects item when request signal is aborted", () => {
      const queue = createQueue();
      const item = createQueueItem({
        config: { headers: {} as unknown as AxiosRequestHeaders, signal: { aborted: true } },
      });

      queue.enqueue(item);
      queue.process(null, "new-token");

      expect(item.reject).toHaveBeenCalledOnce();
      expect(item.resolve).not.toHaveBeenCalled();
    });

    it("clears queue after processing", () => {
      const queue = createQueue();
      queue.enqueue(createQueueItem());
      queue.process(null, "token");

      expect(queue.size()).toBe(0);
    });

    it("handles empty queue gracefully", () => {
      const queue = createQueue();

      expect(() => queue.process(null, "token")).not.toThrow();
      expect(() => queue.process(new Error("fail"), null)).not.toThrow();
    });

    it("splits resolve/reject correctly — aborted items rejected, active items resolved", () => {
      const queue = createQueue();
      const aborted = createQueueItem({
        config: { headers: {} as unknown as AxiosRequestHeaders, signal: { aborted: true } },
      });
      const active = createQueueItem();

      queue.enqueue(aborted);
      queue.enqueue(active);
      queue.process(null, "token");

      expect(aborted.reject).toHaveBeenCalledOnce();
      expect(aborted.resolve).not.toHaveBeenCalled();
      expect(active.resolve).toHaveBeenCalledWith("token");
      expect(active.reject).not.toHaveBeenCalled();
    });
  });

  describe("size", () => {
    it("returns the number of queued items", () => {
      const queue = createQueue();
      expect(queue.size()).toBe(0);

      queue.enqueue(createQueueItem());
      expect(queue.size()).toBe(1);

      queue.enqueue(createQueueItem());
      expect(queue.size()).toBe(2);

      queue.process(null, "token");
      expect(queue.size()).toBe(0);
    });
  });
});
