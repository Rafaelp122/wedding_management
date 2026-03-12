import { useRouteError } from "react-router-dom";

export const GlobalError = () => {
  const error = useRouteError();
  console.error("Erro capturado pelo Router:", error);

  return (
    <div className="flex h-screen w-full flex-col items-center justify-center p-4 text-center bg-background">
      <h2 className="text-2xl font-bold text-destructive mb-2">
        Erro Inesperado
      </h2>
      <p className="text-muted-foreground max-w-md">
        Algo correu mal ao tentar carregar esta secção. Verifica a tua ligação
        ou tenta novamente.
      </p>
      <button
        onClick={() => (window.location.href = "/")}
        className="mt-6 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
      >
        Voltar ao Início
      </button>
    </div>
  );
};
