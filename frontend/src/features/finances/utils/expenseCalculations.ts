/**
 * Calcula o progresso do pagamento de uma despesa baseado no valor pago e no valor total.
 *
 * @param expense Objeto contendo o valor total pago e o valor real da despesa.
 * @returns Progresso do pagamento em percentual (0 a 100).
 */
interface ProgressInput {
  total_paid?: string | number | null;
  actual_amount?: string | number | null;
}

export function calculateExpenseProgress(expense: ProgressInput): number {
  const totalPaid = Number(expense.total_paid ?? 0);
  const actualAmount = Number(expense.actual_amount ?? 0);

  if (actualAmount <= 0) {
    return 0;
  }

  return Math.min(100, Math.round((totalPaid / actualAmount) * 100));
}
