import { beforeEach, describe, expect, it, vi } from "vitest";
import { AxiosError, AxiosHeaders } from "axios";
import { addConnectionErrorInterceptor } from "@/api/interceptors/connection-error";


import * as Sentry from "@sentry/react";

function createMockInstance() {
  const handlers = {
    success: null as ((response: unknown) => unknown) | null,
    error: null as ((error: unknown) => unknown) | null,
  };

  const instance = {
    interceptors: {
      response: {
        use(
          onSuccess: (response: unknown) => unknown,
          onError: (error: unknown) => unknown,
        ) {
          handlers.success = onSuccess;
          handlers.error = onError;
          return 0;
        },
      },
    },
  };

  addConnectionErrorInterceptor(instance as never);

  return handlers;
}

describe("addConnectionErrorInterceptor", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("success handler", () => {
    it("sets Sentry context with X-Request-ID from response headers", () => {
      const handlers = createMockInstance();

      handlers.success?.({
        headers: { "x-request-id": "req-abc-123" },
        status: 200,
        data: {},
        config: {},
        statusText: "OK",
      });

      expect(Sentry.setContext).toHaveBeenCalledWith("request", {
        request_id: "req-abc-123",
      });
    });

    it("does not call Sentry.setContext when X-Request-ID is absent", () => {
      const handlers = createMockInstance();

      handlers.success?.({
        headers: {},
        status: 200,
        data: {},
        config: {},
        statusText: "OK",
      });

      expect(Sentry.setContext).not.toHaveBeenCalled();
    });
  });

  describe("error handler", () => {
    it("captures network error to Sentry", async () => {
      const handlers = createMockInstance();
      const error = new AxiosError("Network Error", "ERR_NETWORK");

      const result = handlers.error?.(error);
      await expect(result).rejects.toBe(error);

      expect(Sentry.captureException).toHaveBeenCalledWith(error, {
        tags: { source: "connection-error-interceptor" },
      });
    });

    it("captures 502 error to Sentry", async () => {
      const handlers = createMockInstance();
      const error = new AxiosError(
        "Bad Gateway",
        "ERR_BAD_RESPONSE",
        undefined,
        undefined,
        {
          status: 502,
          data: {},
          statusText: "Bad Gateway",
          headers: {},
          config: {} as never,
        },
      );

      const result = handlers.error?.(error);
      await expect(result).rejects.toBe(error);

      expect(Sentry.captureException).toHaveBeenCalledWith(error, {
        tags: { source: "connection-error-interceptor" },
      });
    });

    it("captures 503 error to Sentry", async () => {
      const handlers = createMockInstance();
      const error = new AxiosError(
        "Service Unavailable",
        "ERR_BAD_RESPONSE",
        undefined,
        undefined,
        {
          status: 503,
          data: {},
          statusText: "Service Unavailable",
          headers: {},
          config: {} as never,
        },
      );

      const result = handlers.error?.(error);
      await expect(result).rejects.toBe(error);

      expect(Sentry.captureException).toHaveBeenCalledWith(error, {
        tags: { source: "connection-error-interceptor" },
      });
    });

    it("captures 504 error to Sentry", async () => {
      const handlers = createMockInstance();
      const error = new AxiosError(
        "Gateway Timeout",
        "ERR_BAD_RESPONSE",
        undefined,
        undefined,
        {
          status: 504,
          data: {},
          statusText: "Gateway Timeout",
          headers: {},
          config: {} as never,
        },
      );

      const result = handlers.error?.(error);
      await expect(result).rejects.toBe(error);

      expect(Sentry.captureException).toHaveBeenCalledWith(error, {
        tags: { source: "connection-error-interceptor" },
      });
    });

    it("does not capture 400 error to Sentry", async () => {
      const handlers = createMockInstance();
      const error = new AxiosError(
        "Bad Request",
        "ERR_BAD_REQUEST",
        undefined,
        undefined,
        {
          status: 400,
          data: {},
          statusText: "Bad Request",
          headers: {},
          config: {} as never,
        },
      );

      const result = handlers.error?.(error);
      await expect(result).rejects.toBe(error);

      expect(Sentry.captureException).not.toHaveBeenCalled();
    });

    it("does not capture 500 error to Sentry", async () => {
      const handlers = createMockInstance();
      const error = new AxiosError(
        "Internal Server Error",
        "ERR_BAD_RESPONSE",
        undefined,
        undefined,
        {
          status: 500,
          data: {},
          statusText: "Internal Server Error",
          headers: {},
          config: {} as never,
        },
      );

      const result = handlers.error?.(error);
      await expect(result).rejects.toBe(error);

      expect(Sentry.captureException).not.toHaveBeenCalled();
    });

    it("sets Sentry context with X-Request-ID from error response headers", async () => {
      const handlers = createMockInstance();
      const error = new AxiosError("Network Error", "ERR_NETWORK");
      error.response = {
        status: 502,
        data: {},
        statusText: "Bad Gateway",
        headers: new AxiosHeaders({ "x-request-id": "err-req-789" }),
        config: {} as never,
      };

      await expect(handlers.error?.(error)).rejects.toBe(error);

      expect(Sentry.setContext).toHaveBeenCalledWith("request", {
        request_id: "err-req-789",
      });
    });

    it("does not call Sentry.setContext when error has no X-Request-ID", async () => {
      const handlers = createMockInstance();
      const error = new AxiosError("Network Error", "ERR_NETWORK");

      await expect(handlers.error?.(error)).rejects.toBe(error);

      expect(Sentry.setContext).not.toHaveBeenCalled();
    });

    it("rejects with the original error for non-connection errors", async () => {
      const handlers = createMockInstance();
      const error = new AxiosError(
        "Not Found",
        "ERR_BAD_REQUEST",
        undefined,
        undefined,
        {
          status: 404,
          data: {},
          statusText: "Not Found",
          headers: {},
          config: {} as never,
        },
      );

      const result = handlers.error?.(error);
      await expect(result).rejects.toBe(error);
      expect(Sentry.captureException).not.toHaveBeenCalled();
    });
  });
});
