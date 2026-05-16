import { AxiosError } from "axios";
import type { FailedQueueItem } from "@/api/types/queue";

/**
 * Cria uma fila mutável para requisições que chegaram durante um refresh
 * de token. O objeto retornado encapsula todo o estado da fila, expondo
 * apenas `enqueue` e `process`.
 *
 * `process(error, token)` drena a fila: se `error` não for nulo, todos os
 * itens são rejeitados com ele; se `token` não for nulo, todos os itens
 * são resolvidos (requisições abortadas são rejeitadas em vez disso).
 * Após o processamento, a fila é limpa.
 */
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
