import {
  useFinancesBudgetsForWedding,
  useFinancesBudgetsPartialUpdate,
  useFinancesCategoriesList,
} from "@/api/generated/v1/endpoints/finances/finances";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useQueryClient } from "@tanstack/react-query";
import { AlertCircle, DollarSign, Save, TrendingUp, X } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface WeddingBudgetProps {
  weddingUuid: string;
}

export function WeddingBudget({ weddingUuid }: WeddingBudgetProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTotal, setEditTotal] = useState<string>("");
  const queryClient = useQueryClient();

  const {
    data: budgetResponse,
    isLoading: isLoadingBudget,
    error: budgetError,
  } = useFinancesBudgetsForWedding(weddingUuid);

  const { data: categoriesResponse, isLoading: isLoadingCategories } =
    useFinancesCategoriesList({ wedding_id: weddingUuid });

  const updateBudgetMutation = useFinancesBudgetsPartialUpdate();

  const budget = budgetResponse?.data;
  const categories = categoriesResponse?.data?.items || [];

  const handleEditInit = () => {
    if (budget) {
      setEditTotal(budget.total_estimated?.toString() || "0");
      setIsEditing(true);
    }
  };

  const handleSave = async () => {
    if (!budget) return;
    try {
      await updateBudgetMutation.mutateAsync({
        uuid: budget.uuid,
        data: {
          total_estimated: editTotal,
        },
      });
      toast.success("Orçamento atualizado com sucesso!");
      setIsEditing(false);
      queryClient.invalidateQueries();
    } catch (error) {
      toast.error("Falha ao atualizar orçamento.");
    }
  };

  if (isLoadingBudget || isLoadingCategories) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (budgetError || !budget) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Erro ao carregar orçamento do casamento.
        </AlertDescription>
      </Alert>
    );
  }

  const totalAllocated = categories.reduce(
    (acc, cat) => acc + Number(cat.allocated_budget || 0),
    0,
  );
  const totalSpent = Number(budget.total_spent || 0);
  const totalEstimated = Number(budget.total_estimated || 0);

  const progressPercentage =
    totalEstimated > 0 ? (totalSpent / totalEstimated) * 100 : 0;
  const progressColor =
    progressPercentage > 100
      ? "bg-red-500"
      : progressPercentage > 80
        ? "bg-yellow-500"
        : "bg-green-500";

  return (
    <div className="space-y-6">
      {/* Resumo do Orçamento */}
      <Card>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Orçamento Total
              </CardTitle>
              <CardDescription>
                Tabela de gastos planejados e alocados do evento
              </CardDescription>
            </div>
            {!isEditing && (
              <Button variant="outline" size="sm" onClick={handleEditInit}>
                Editar Teto
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <div className="flex items-end gap-4 bg-muted/50 p-4 rounded-lg">
              <div className="grid gap-2 flex-1">
                <Label htmlFor="total">Novo Valor Estimado (R$)</Label>
                <Input
                  id="total"
                  type="number"
                  step="0.01"
                  value={editTotal}
                  onChange={(e) => setEditTotal(e.target.value)}
                  className="max-w-xs bg-background"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleSave}
                  disabled={updateBudgetMutation.isPending}
                >
                  {updateBudgetMutation.isPending ? (
                    "Salvando..."
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" /> Salvar
                    </>
                  )}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setIsEditing(false)}
                >
                  <X className="w-4 h-4 mr-2" /> Cancelar
                </Button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">
                  Teto Estimado
                </p>
                <p className="text-3xl font-bold">
                  R${" "}
                  {totalEstimated.toLocaleString("pt-BR", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">
                  Total Alocado
                </p>
                <p className="text-3xl font-semibold text-primary">
                  R${" "}
                  {totalAllocated.toLocaleString("pt-BR", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">
                  Status de Gastos
                </p>
                <div className="h-4 w-full bg-secondary rounded-full overflow-hidden mt-3">
                  <div
                    className={`h-full ${progressColor} transition-all duration-500`}
                    style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                  />
                </div>
                <p className="text-xs text-right mt-1 text-muted-foreground">
                  R${" "}
                  {totalSpent.toLocaleString("pt-BR", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}{" "}
                  ({progressPercentage.toFixed(1)}%) gasto
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Lista de Categorias */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Categorias de Custo
          </CardTitle>
          <CardDescription>
            Divisão do teto orçamentário por centro de custos (áreas do
            casamento)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {categories.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p className="mb-2">Nenhuma categoria encontrada.</p>
              <p className="text-xs">
                Adicione categorias para começar a gerenciar o orçamento.
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Descrição / Notas</TableHead>
                  <TableHead className="text-right">
                    Orçamento Alocado
                  </TableHead>
                  <TableHead className="text-right">Total Gasto</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {categories.map((cat: any) => (
                  <TableRow key={cat.uuid}>
                    <TableCell className="font-medium">{cat.name}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {cat.description || "N/A"}
                    </TableCell>
                    <TableCell className="text-right">
                      R${" "}
                      {Number(cat.allocated_budget).toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </TableCell>{" "}
                    <TableCell className="text-right">
                      R${" "}
                      {Number(cat.total_spent || 0).toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </TableCell>{" "}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Informações gerais do projeto */}
      {budget.notes && (
        <Card>
          <CardHeader>
            <CardTitle>Observações Globais</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm whitespace-pre-wrap">{budget.notes}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
