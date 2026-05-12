import { TrendingUp } from "lucide-react";

import type { BudgetCategoryOut } from "@/api/generated/v1/models/budgetCategoryOut";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";

interface WeddingBudgetCategoriesCardProps {
  categories: BudgetCategoryOut[];
}

export function WeddingBudgetCategoriesCard({
  categories,
}: WeddingBudgetCategoriesCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Categorias de Custo
        </CardTitle>
        <CardDescription>
          Divisão do teto orçamentário por centro de custos (áreas do casamento)
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
                <TableHead className="text-right">Orçamento Alocado</TableHead>
                <TableHead className="text-right">Total Gasto</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {categories.map((category) => (
                <TableRow key={category.uuid}>
                  <TableCell className="font-medium">{category.name}</TableCell>
                  <TableCell className="text-muted-foreground text-sm">
                    {category.description || "N/A"}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    R$ {formatCurrencyBR(Number(category.allocated_budget))}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    R$ {formatCurrencyBR(Number(category.total_spent || 0))}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
