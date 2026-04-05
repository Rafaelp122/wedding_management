import { useState } from "react";
import { useFinancesBudgetsForWedding } from "@/api/generated/v1/endpoints/finances/finances";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { DollarSign, TrendingUp, AlertCircle } from "lucide-react";

interface WeddingBudgetProps {
  weddingUuid: string;
}

export function WeddingBudget({ weddingUuid }: WeddingBudgetProps) {
  const [isEditing, setIsEditing] = useState(false);

  const {
    data: response,
    isLoading,
    error,
  } = useFinancesBudgetsForWedding(weddingUuid);

  const budget = response?.data;

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-50 w-full" />
        <Skeleton className="h-75 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Erro ao carregar orçamento: {error.message}
        </AlertDescription>
      </Alert>
    );
  }

  if (!budget) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Nenhum orçamento encontrado para este casamento.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Card principal com orçamento total */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Orçamento Total Estimado
              </CardTitle>
              <CardDescription>
                Valor planejado para todo o evento
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(!isEditing)}
            >
              {isEditing ? "Cancelar" : "Editar"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-bold">
            R${" "}
            {Number(budget.total_estimated).toLocaleString("pt-BR", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </div>
          {budget.total_estimated === "0.00" && (
            <p className="text-sm text-muted-foreground mt-2">
              Defina um valor estimado para começar a planejar seu orçamento
            </p>
          )}
        </CardContent>
      </Card>

      {/* Placeholder para categorias */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Categorias de Orçamento
          </CardTitle>
          <CardDescription>
            Distribua seu orçamento entre as diferentes categorias
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <p className="mb-2">Categorias de orçamento em breve...</p>
            <p className="text-xs">
              Aqui você poderá alocar valores para Buffet, Decoração,
              Fotografia, etc.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Informações do budget */}
      {budget.notes && (
        <Card>
          <CardHeader>
            <CardTitle>Observações</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{budget.notes}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
