import { DollarSign, Save, X } from "lucide-react";

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
import { formatCurrencyBR } from "@/features/shared/utils/formatters";

interface WeddingBudgetSummaryCardProps {
  isEditing: boolean;
  editTotal: string;
  isSaving: boolean;
  totalEstimated: number;
  totalAllocated: number;
  totalSpent: number;
  progressPercentage: number;
  progressColor: string;
  onEditTotalChange: (value: string) => void;
  onStartEdit: () => void;
  onSave: () => void;
  onCancelEdit: () => void;
}

export function WeddingBudgetSummaryCard({
  isEditing,
  editTotal,
  isSaving,
  totalEstimated,
  totalAllocated,
  totalSpent,
  progressPercentage,
  progressColor,
  onEditTotalChange,
  onStartEdit,
  onSave,
  onCancelEdit,
}: WeddingBudgetSummaryCardProps) {
  return (
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
            <Button variant="outline" size="sm" onClick={onStartEdit}>
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
                onChange={(event) => onEditTotalChange(event.target.value)}
                className="max-w-xs bg-background"
              />
            </div>
            <div className="flex gap-2">
              <Button size="sm" onClick={onSave} disabled={isSaving}>
                {isSaving ? (
                  "Salvando..."
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" /> Salvar
                  </>
                )}
              </Button>
              <Button size="sm" variant="ghost" onClick={onCancelEdit}>
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
              <p className="text-3xl font-bold tabular-nums">
                R$ {formatCurrencyBR(totalEstimated)}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                Total Alocado
              </p>
              <p className="text-3xl font-semibold text-primary tabular-nums">
                R$ {formatCurrencyBR(totalAllocated)}
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
              <p className="text-xs text-right mt-1 text-muted-foreground tabular-nums">
                R$ {formatCurrencyBR(totalSpent)} ({progressPercentage.toFixed(1)}
                %) gasto
              </p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
