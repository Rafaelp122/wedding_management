import { describe, expect, it, vi } from "vitest";
import { toast } from "sonner";
import { createMutationCallbacks } from "./use-mutation-toast";

/**
 * Testes para createMutationCallbacks.
 *
 * Nota: não mockamos getApiErrorInfo pois é uma função pura interna que
 * já possui cobertura própria. Testamos o comportamento de ponta a ponta
 * do hook, verificando as chamadas reais ao toast do Sonner (já mockado
 * globalmente em test-setup.ts).
 */
describe("createMutationCallbacks", () => {
  it("deve acionar toast.success e chamar onSuccess quando a operação é bem-sucedida", () => {
    const onSuccessMock = vi.fn();
    const callbacks = createMutationCallbacks({
      successMsg: "Operação realizada!",
      onSuccess: onSuccessMock,
    });

    const mockData = { id: 1, name: "Test" };
    callbacks.onSuccess(mockData);

    expect(toast.success).toHaveBeenCalledWith("Operação realizada!");
    expect(onSuccessMock).toHaveBeenCalledWith(mockData);
  });

  it("deve acionar toast.error com a mensagem do Error quando a operação falha", () => {
    const mockError = new Error("Erro interno do servidor");
    const callbacks = createMutationCallbacks({
      successMsg: "Sucesso",
      fallbackErrorMsg: "Erro customizado",
    });

    callbacks.onError(mockError);

    // getApiErrorInfo retorna error.message diretamente para instâncias de Error não-Axios
    expect(toast.error).toHaveBeenCalledWith("Erro interno do servidor");
  });

  it("deve usar a mensagem de fallback quando o erro não possui mensagem", () => {
    const callbacks = createMutationCallbacks({
      successMsg: "Sucesso",
      fallbackErrorMsg: "Falha ao realizar a operação.",
    });

    // Erro sem mensagem (ex: objeto genérico lançado)
    callbacks.onError({});

    expect(toast.error).toHaveBeenCalledWith("Falha ao realizar a operação.");
  });

  it("deve usar a mensagem de fallback padrão quando fallbackErrorMsg não é fornecido", () => {
    const callbacks = createMutationCallbacks({
      successMsg: "Sucesso",
    });

    callbacks.onError({});

    expect(toast.error).toHaveBeenCalledWith("Não foi possível concluir a operação.");
  });

  it("deve chamar onSuccess sem o callback opcional sem erros", () => {
    const callbacks = createMutationCallbacks({
      successMsg: "Feito!",
    });

    expect(() => callbacks.onSuccess({ data: "any" })).not.toThrow();
    expect(toast.success).toHaveBeenCalledWith("Feito!");
  });
});
