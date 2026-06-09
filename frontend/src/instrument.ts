import React from "react";
import * as Sentry from "@sentry/react";
import {
  useLocation,
  useNavigationType,
  createRoutesFromChildren,
  matchRoutes,
} from "react-router-dom";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  sendDefaultPii: false,

  tracePropagationTargets: ["localhost", /^\//, /^https:\/\/[a-z0-9-]+\.run\.app/],

  integrations: [
    Sentry.reactRouterV7BrowserTracingIntegration({
      useEffect: React.useEffect,
      useLocation,
      useNavigationType,
      createRoutesFromChildren,
      matchRoutes,
    }),
    Sentry.replayIntegration({
      maskAllText: !import.meta.env.DEV,
      blockAllMedia: !import.meta.env.DEV,
    }),
  ],

  // Tracing configuration
  tracesSampleRate: import.meta.env.DEV ? 1.0 : 0.1,

  // Session Replay configuration
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  beforeSend(event, hint) {
    const error = hint?.originalException;
    if (error && typeof error === "object") {
      // Ignore network errors or aborted requests
      if ("message" in error && (error.message === "Network Error" || error.message === "Connection refused")) {
        return null;
      }
      // Ignore Axios errors with expected status codes (401, 403, 404, 422)
      if ("isAxiosError" in error && error.isAxiosError) {
        const status = (error as { response?: { status?: number } }).response?.status;
        if (status && [401, 403, 404, 422].includes(status)) {
          return null;
        }
      }
      // Cancelled requests (Axios CancelToken / AbortController)
      if ("name" in error && error.name === "CanceledError") {
        return null;
      }
    }
    return event;
  },
});
