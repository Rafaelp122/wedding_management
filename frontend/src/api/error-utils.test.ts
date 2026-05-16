import { describe, expect, it } from "vitest";
import { getApiErrorInfo } from "@/api/error-utils";
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
