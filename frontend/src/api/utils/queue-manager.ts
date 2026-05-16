import { AxiosError } from "axios";
import type { FailedQueueItem } from "@/api/types/queue";

export function createQueue() {
  let queue: FailedQueueItem[] = [];

  return {
    enqueue(item: FailedQueueItem) {
      queue.push(item);
    },

    size() {
      return queue.length;
    },

    process(error: Error | null, token: string | null) {
      queue.forEach((item) => {
        if (error) {
          item.reject(error);
        } else if (token) {
          if (item.config.signal?.aborted) {
            item.reject(
              new AxiosError(
                "Requisição abortada na fila",
                AxiosError.ERR_CANCELED,
                item.config,
              ),
            );
          } else {
            item.resolve(token);
          }
        }
      });
      queue = [];
    },
  };
}
