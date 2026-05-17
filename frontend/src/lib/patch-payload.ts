/**
 * Constrói um objeto de patch contendo apenas os campos que diferem entre
 * `original` e `modified`. Se nenhum campo mudou, retorna um objeto vazio.
 *
 * Útil para mutações PATCH que só devem enviar dados alterados ao backend.
 *
 * A função é intencionalmente simples:
 * - Usa comparação estrita (`!==`) — se o tipo mudar, o campo é incluído,
 *   que é o comportamento desejado para PATCH (o backend recebe o novo valor).
 * - `keys` funciona como allowlist de segurança — campos fora da lista
 *   nunca entram no payload, mesmo que tenham mudado.
 * - Objetos planos (`Record<string, unknown>`) cobrem todos os DTOs da API;
 *   objetos aninhados ou arrays não são necessários no domínio atual.
 *
 * @param original — dados da entidade antes da edição
 * @param modified — dados do formulário após edição do usuário
 * @param keys     — lista de chaves a comparar (allowlist)
 * @returns objeto parcial contendo apenas os campos que mudaram
 */
export function buildPatchPayload<
  T extends Record<string, unknown>,
  K extends keyof T,
>(original: T, modified: T, keys: readonly K[]): Partial<T> {
  const payload: Partial<T> = {};
  for (const key of keys) {
    if (modified[key] !== original[key]) {
      payload[key] = modified[key];
    }
  }
  return payload;
}
