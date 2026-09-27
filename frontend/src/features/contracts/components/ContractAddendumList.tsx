import { memo, useMemo, useState } from "react";
import { Plus, CheckCircle } from "lucide-react";
import type { ContractAddendumOut } from "@/api/generated/v1/models/contractAddendumOut";
import { formatCurrencyBR, formatDateBR } from "@/lib/formatters";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { STATUS_STYLES, STATUS_LABELS } from "@/features/contracts/constants";
import {
  ADDENDUM_FILTER_OPTIONS,
  countAddendumsByStatus,
  filterAddendumsByStatus,
  sumAddendumAmounts,
  type AddendumStatusFilter,
} from "../utils/addendum-helpers";

export interface ContractAddendumListProps {
  addendums: ContractAddendumOut[];
  onSignAddendum?: (addendum: ContractAddendumOut) => void;
  onCreateAddendum?: () => void;
}

export const ContractAddendumList = memo(function ContractAddendumList({
  addendums,
  onSignAddendum,
  onCreateAddendum,
}: ContractAddendumListProps) {
  const [statusFilter, setStatusFilter] = useState<AddendumStatusFilter>("ALL");

  const counts = useMemo(() => countAddendumsByStatus(addendums), [addendums]);
  const visibleAddendums = useMemo(
    () => filterAddendumsByStatus(addendums, statusFilter),
    [addendums, statusFilter],
  );
  const visibleSubtotal = useMemo(
    () => sumAddendumAmounts(visibleAddendums),
    [visibleAddendums],
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold">Termos Aditivos</h4>
        {onCreateAddendum && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="h-7 text-xs"
            onClick={onCreateAddendum}
          >
            <Plus className="size-3 mr-1" />
            Criar Aditivo
          </Button>
        )}
      </div>

      {addendums.length === 0 ? (
        <div className="rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground">
          Nenhum aditivo registrado para este contrato.
        </div>
      ) : (
        <>
          <div className="flex flex-wrap gap-1.5" role="group" aria-label="Filtrar aditivos por status">
            {ADDENDUM_FILTER_OPTIONS.map((opt) => {
              const isActive = statusFilter === opt.value;
              const count = counts[opt.value];
              return (
                <Button
                  key={opt.value}
                  type="button"
                  variant={isActive ? "default" : "outline"}
                  size="sm"
                  className="h-6 px-2 text-[11px]"
                  onClick={() => setStatusFilter(opt.value)}
                  aria-pressed={isActive}
                >
                  {opt.label} ({count})
                </Button>
              );
            })}
          </div>

          {visibleAddendums.length === 0 ? (
            <div className="rounded-md border border-dashed p-4 text-center text-sm text-muted-foreground">
              Nenhum aditivo com este status.
            </div>
          ) : (
        <div className="rounded-md border overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50 text-muted-foreground">
                <th className="text-left px-3 py-2 font-medium text-xs">
                  Justificativa
                </th>
                <th className="text-left px-3 py-2 font-medium text-xs w-28">
                  Data
                </th>
                <th className="text-right px-3 py-2 font-medium text-xs w-28">
                  Valor
                </th>
                <th className="text-center px-3 py-2 font-medium text-xs w-24">
                  Status
                </th>
                {onSignAddendum && (
                  <th className="text-center px-3 py-2 font-medium text-xs w-20">
                    Ações
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {visibleAddendums.map((addendum) => (
                <tr
                  key={addendum.uuid}
                  className="border-b last:border-0 hover:bg-muted/20 transition-colors"
                >
                  <td className="px-3 py-2 max-w-[200px]">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span className="truncate block font-medium cursor-help">
                          {addendum.justification}
                        </span>
                      </TooltipTrigger>
                      <TooltipContent side="top" className="max-w-xs">
                        {addendum.justification}
                      </TooltipContent>
                    </Tooltip>
                  </td>
                  <td className="px-3 py-2 text-xs text-muted-foreground whitespace-nowrap">
                    {addendum.signed_date
                      ? formatDateBR(addendum.signed_date)
                      : formatDateBR(addendum.created_at)}
                  </td>
                  <td className="px-3 py-2 text-right font-medium whitespace-nowrap">
                    R$ {formatCurrencyBR(Number(addendum.amount))}
                  </td>
                  <td className="px-3 py-2 text-center whitespace-nowrap">
                    <Badge
                      className={`text-[10px] h-5 ${STATUS_STYLES[addendum.status] || ""}`}
                    >
                      {STATUS_LABELS[addendum.status] || addendum.status}
                    </Badge>
                  </td>
                  {onSignAddendum && (
                    <td className="px-3 py-2 text-center whitespace-nowrap">
                      {addendum.status === "PENDING" && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="h-6 px-2 text-xs text-green-700 hover:text-green-800 hover:bg-green-50"
                          onClick={() => onSignAddendum(addendum)}
                          title="Assinar aditivo"
                        >
                          <CheckCircle className="size-3.5 mr-1" />
                          Assinar
                        </Button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
          )}

          <p className="text-xs text-muted-foreground text-right">
            Subtotal exibido:{" "}
            <strong className="text-foreground" data-testid="addendum-subtotal">
              R$ {formatCurrencyBR(visibleSubtotal)}
            </strong>
          </p>
        </>
      )}
    </div>
  );
});
