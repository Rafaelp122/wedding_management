import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { toast } from "sonner";

interface EmptyWeddingsStateProps {
  onCreateClick: () => void;
}

export function EmptyWeddingsState({ onCreateClick }: EmptyWeddingsStateProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center text-center px-8 py-12 max-w-xl mx-auto">
      <div className="relative w-44 h-44 mb-6 flex items-center justify-center flex-shrink-0">
        <div className="absolute inset-4 rounded-full bg-primary/10 dark:bg-primary/15 blur-xl" />
        <svg
          className="w-full h-full text-primary dark:text-aura-300 relative z-10"
          viewBox="0 0 100 100"
          fill="none"
        >
          <path
            d="M25 80V45C25 31.1929 36.1929 20 50 20C63.8071 20 75 31.1929 75 45V80"
            stroke="currentColor"
            strokeWidth={1.5}
            strokeLinecap="round"
            strokeDasharray="2 3"
          />
          <path
            d="M32 80V48C32 39.1634 39.1634 32 50 32C60.8366 32 68 39.1634 68 48V80"
            stroke="currentColor"
            strokeWidth={1}
            strokeLinecap="round"
          />
          <path
            d="M20 75C21 65 26 50 35 48"
            stroke="currentColor"
            strokeWidth={1}
            strokeLinecap="round"
          />
          <circle cx="35" cy="48" r="1.5" fill="currentColor" />
          <path
            d="M80 75C79 65 74 50 65 48"
            stroke="currentColor"
            strokeWidth={1}
            strokeLinecap="round"
          />
          <circle cx="65" cy="48" r="1.5" fill="currentColor" />
          <circle
            cx="46"
            cy="74"
            r="5"
            stroke="currentColor"
            strokeWidth={1.2}
          />
          <circle
            cx="54"
            cy="74"
            r="5"
            stroke="currentColor"
            strokeWidth={1.2}
          />
        </svg>
      </div>

      <div className="space-y-3">
        <h2 className="font-display text-xl sm:text-2xl font-bold tracking-tight">
          Sua tela em branco para criar memórias.
        </h2>
        <p className="text-sm text-muted-foreground leading-relaxed font-light">
          Cada grande assessoria de casamentos começa com a primeira história.
          Cadastre o seu primeiro casal para liberar checklists por fases,
          cronogramas operacionais do grande dia e faturamento sequencial de
          fornecedores.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-3 mt-8 w-full sm:w-auto">
        <Button
          onClick={onCreateClick}
          size="lg"
          className="gap-2 w-full sm:w-auto"
        >
          <Plus className="size-4" />
          Cadastrar Primeiro Casamento
        </Button>
        <Button
          variant="outline"
          size="lg"
          className="w-full sm:w-auto"
          onClick={() => toast.info("Demonstração em breve!")}
        >
          Carregar Exemplo Prático
        </Button>
      </div>
    </div>
  );
}
