import { useRouteError } from "react-router-dom";
import * as Sentry from "@sentry/react";

export const GlobalError = () => {
  const error = useRouteError();
  const isDev = import.meta.env.DEV;

  if (isDev) {
    console.error(error);
  }

  if (error instanceof Error) {
    Sentry.captureException(error);
  } else {
    Sentry.captureMessage(`Non-Error route error: ${String(error)}`, "warning");
  }

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-center p-4 text-center bg-background">
      <h2 className="text-2xl font-bold text-destructive mb-2">
        Erro Inesperado
      </h2>
      <p className="text-muted-foreground max-w-md">
        Algo deu errado ao carregar esta seção. Verifique sua conexão ou tente
        novamente.
      </p>

      {isDev && error instanceof Error && (
        <div className="mt-6 w-full max-w-3xl">
          <p className="text-sm font-medium text-destructive mb-2 text-left">
            {error.message}
          </p>
          <pre className="text-left text-xs bg-muted p-4 rounded-md border overflow-auto max-h-96 whitespace-pre-wrap">
            {error.stack}
          </pre>
        </div>
      )}

      <button
        onClick={() => (window.location.href = "/")}
        className="mt-6 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
      >
        Voltar ao Início
      </button>
    </div>
  );
};
