import { describe, expect, it, vi } from "vitest";
import { toast } from "sonner";
import { getApiErrorInfo } from "@/api/error-utils";
import { createMutationCallbacks } from "./use-mutation-toast";

// Mock the getApiErrorInfo function
vi.mock("@/api/error-utils", () => ({
  getApiErrorInfo: vi.fn(),
}));

describe("createMutationCallbacks", () => {
  it("should trigger toast.success and call onSuccess callback when operation succeeds", () => {
    const onSuccessMock = vi.fn();
    const callbacks = createMutationCallbacks({
      successMsg: "Operação realizada!",
      onSuccess: onSuccessMock,
    });

    const mockData = { id: 1, name: "Test" };
    callbacks.onSuccess(mockData);

    // Assert global sonner mock has been called
    expect(toast.success).toHaveBeenCalledWith("Operação realizada!");
    expect(onSuccessMock).toHaveBeenCalledWith(mockData);
  });

  it("should trigger toast.error using the message resolved from getApiErrorInfo when operation fails", () => {
    const mockError = new Error("Erro interno");
    vi.mocked(getApiErrorInfo).mockReturnValue({
      message: "Mensagem de erro da API",
      status: 500,
    });

    const callbacks = createMutationCallbacks({
      successMsg: "Sucesso",
      fallbackErrorMsg: "Erro customizado",
    });

    callbacks.onError(mockError);

    expect(getApiErrorInfo).toHaveBeenCalledWith(mockError, "Erro customizado");
    expect(toast.error).toHaveBeenCalledWith("Mensagem de erro da API");
  });

  it("should use default fallback error message if not provided", () => {
    const mockError = new Error("Erro");
    vi.mocked(getApiErrorInfo).mockReturnValue({
      message: "Não foi possível concluir a operação.",
      status: 400,
    });

    const callbacks = createMutationCallbacks({
      successMsg: "Sucesso",
    });

    callbacks.onError(mockError);

    expect(getApiErrorInfo).toHaveBeenCalledWith(mockError, "Não foi possível concluir a operação.");
    expect(toast.error).toHaveBeenCalledWith("Não foi possível concluir a operação.");
  });
});
