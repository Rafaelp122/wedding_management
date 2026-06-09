import { beforeEach, describe, expect, it, vi } from "vitest";
import { getApiErrorInfo, mapErrorsToForm } from "@/api/error-utils";
import type { ApiErrorInfo } from "@/api/types/errors";
import { AxiosError } from "axios";

function createAxiosError(
  status: number,
  data: Record<string, unknown> = {},
): AxiosError {
  const error = new AxiosError(
    "Request failed",
    "ERR_BAD_REQUEST",
    undefined,
    undefined,
    {
      status,
      data,
      statusText: "Error",
      headers: {},
      config: {} as never,
    },
  );
  return error;
}

describe("getApiErrorInfo", () => {
  it("returns fallback for non-Axios errors", () => {
    const result = getApiErrorInfo(new Error("boom"));
    expect(result).toEqual<ApiErrorInfo>({
      message: "Não foi possível concluir a operação.",
    });
  });

  it("returns custom fallback for non-Axios errors", () => {
    const result = getApiErrorInfo(new Error("boom"), "deu ruim");
    expect(result.message).toBe("deu ruim");
  });

  it("returns network error message for Network Error", () => {
    const error = new AxiosError("Network Error", "ERR_NETWORK");
    const result = getApiErrorInfo(error);
    expect(result.message).toBe(
      "Não foi possível conectar ao servidor. Por favor, tente novamente mais tarde.",
    );
  });

  it("returns network error message when response is missing", () => {
    const error = new AxiosError("Request failed", "ERR_BAD_REQUEST");
    const result = getApiErrorInfo(error);
    expect(result.message).toBe(
      "Não foi possível conectar ao servidor. Por favor, tente novamente mais tarde.",
    );
  });

  it("returns status-based message for 401", () => {
    const result = getApiErrorInfo(createAxiosError(401));
    expect(result.status).toBe(401);
    expect(result.message).toBe("Sua sessão expirou. Faça login novamente.");
  });

  it("returns status-based message for 403", () => {
    const result = getApiErrorInfo(createAxiosError(403));
    expect(result.message).toBe(
      "Você não tem permissão para executar esta ação.",
    );
  });

  it("returns status-based message for 409", () => {
    const result = getApiErrorInfo(createAxiosError(409));
    expect(result.message).toBe(
      "Conflito de dados. Atualize a página e tente novamente.",
    );
  });

  it("returns status-based message for 422", () => {
    const result = getApiErrorInfo(createAxiosError(422));
    expect(result.message).toBe(
      "Alguns dados enviados são inválidos. Revise e tente novamente.",
    );
  });

  it("returns detail from response data", () => {
    const result = getApiErrorInfo(
      createAxiosError(400, { detail: "Invalid input" }),
    );
    expect(result.message).toBe("Invalid input");
  });

  it("returns Pydantic validation detail with field name", () => {
    const result = getApiErrorInfo(
      createAxiosError(422, {
        detail: [
          { type: "value_error", loc: ["body", "email"], msg: "Invalid email" },
        ],
      }),
    );
    expect(result.message).toBe("email: Invalid email");
  });

  it("returns Pydantic validation detail without body prefix", () => {
    const result = getApiErrorInfo(
      createAxiosError(422, {
        detail: [
          { type: "value_error", loc: ["body"], msg: "Request body required" },
        ],
      }),
    );
    expect(result.message).toBe("Request body required");
  });

  it("returns message field from response data", () => {
    const result = getApiErrorInfo(
      createAxiosError(400, { message: "Something went wrong" }),
    );
    expect(result.message).toBe("Something went wrong");
  });

  it("returns code from response data", () => {
    const result = getApiErrorInfo(
      createAxiosError(400, {
        message: "Error",
        code: "INVALID_TOKEN",
      }),
    );
    expect(result.code).toBe("INVALID_TOKEN");
  });

  it("returns first field error when no detail/message", () => {
    const result = getApiErrorInfo(
      createAxiosError(400, { bride_name: ["Este campo é obrigatório"] }),
    );
    expect(result.message).toBe("Este campo é obrigatório");
  });

  it("returns first field error when field value is a string", () => {
    const result = getApiErrorInfo(
      createAxiosError(400, { email: "Endereço de email inválido" }),
    );
    expect(result.message).toBe("Endereço de email inválido");
  });

  it("skips detail/message/code fields in field error extraction", () => {
    const result = getApiErrorInfo(
      createAxiosError(400, {
        detail: "General",
        message: "General",
        code: "X",
        name: ["Required"],
      }),
    );
    expect(result.message).toBe("General");
  });

  it("returns fallback for unknown status code", () => {
    const result = getApiErrorInfo(createAxiosError(418));
    expect(result.message).toBe("Não foi possível concluir a operação.");
  });
});

describe("mapErrorsToForm", () => {
  const mockSetError = vi.fn();

  beforeEach(() => {
    mockSetError.mockClear();
  });

  it("returns false for non-Axios errors", () => {
    const result = mapErrorsToForm(new Error("boom"), mockSetError);
    expect(result).toBe(false);
    expect(mockSetError).not.toHaveBeenCalled();
  });

  it("returns false for Axios errors without response", () => {
    const error = new AxiosError("Network Error", "ERR_NETWORK");
    const result = mapErrorsToForm(error, mockSetError);
    expect(result).toBe(false);
    expect(mockSetError).not.toHaveBeenCalled();
  });

  it("maps Pydantic validation errors to form fields", () => {
    const error = createAxiosError(422, {
      detail: [
        { type: "value_error", loc: ["body", "email"], msg: "Invalid email format" },
        { type: "missing", loc: ["body", "password"], msg: "Field required" },
      ],
    });

    const result = mapErrorsToForm(error, mockSetError);
    expect(result).toBe(true);
    expect(mockSetError).toHaveBeenCalledTimes(2);
    expect(mockSetError).toHaveBeenCalledWith("email", {
      type: "server",
      message: "Invalid email format",
    });
    expect(mockSetError).toHaveBeenCalledWith("password", {
      type: "server",
      message: "Field required",
    });
  });

  it("skips Pydantic errors with 'body' as field name", () => {
    const error = createAxiosError(422, {
      detail: [
        { type: "missing", loc: ["body"], msg: "Request body required" },
      ],
    });

    const result = mapErrorsToForm(error, mockSetError);
    expect(result).toBe(false);
    expect(mockSetError).not.toHaveBeenCalled();
  });

  it("maps Django field errors to form fields", () => {
    const error = createAxiosError(400, {
      email: ["Este campo é obrigatório"],
      name: ["Nome muito curto"],
    });

    const result = mapErrorsToForm(error, mockSetError);
    expect(result).toBe(true);
    expect(mockSetError).toHaveBeenCalledWith("email", {
      type: "server",
      message: "Este campo é obrigatório",
    });
    expect(mockSetError).toHaveBeenCalledWith("name", {
      type: "server",
      message: "Nome muito curto",
    });
  });

  it("skips reserved keys detail, message, code", () => {
    const error = createAxiosError(400, {
      detail: "General error",
      message: "Error",
      code: "ERR",
      email: ["Invalid email"],
    });

    const result = mapErrorsToForm(error, mockSetError);
    expect(result).toBe(true);
    expect(mockSetError).toHaveBeenCalledTimes(1);
    expect(mockSetError).toHaveBeenCalledWith("email", {
      type: "server",
      message: "Invalid email",
    });
  });

  it("returns false when no mappable errors exist", () => {
    const error = createAxiosError(400, {
      detail: "Something went wrong",
      message: "Error",
      code: "ERR",
    });

    const result = mapErrorsToForm(error, mockSetError);
    expect(result).toBe(false);
    expect(mockSetError).not.toHaveBeenCalled();
  });

  it("handles string field errors", () => {
    const error = createAxiosError(400, {
      email: "Endereço de email inválido",
    });

    const result = mapErrorsToForm(error, mockSetError);
    expect(result).toBe(true);
    expect(mockSetError).toHaveBeenCalledWith("email", {
      type: "server",
      message: "Endereço de email inválido",
    });
  });
});
