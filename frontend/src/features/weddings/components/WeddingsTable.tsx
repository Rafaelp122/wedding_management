import { memo } from "react";
import {
  getWeddingStatusBadgeStyle,
  getWeddingStatusLabel,
  getWeddingInitials,
  getWeddingAvatarStyle,
} from "@/features/weddings/utils/wedding-status";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import { WeddingStatusEnum } from "@/api/generated/v1/models/weddingStatusEnum";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatDateBR, formatCurrencyBRCompact } from "@/lib/formatters";
import { cn } from "@/lib/utils";
import { Calendar, Pencil, Trash2, Eye, Check, AlertTriangle } from "lucide-react";

interface WeddingsTableProps {
  weddings: WeddingOut[];
  pageSize: number;
  onWeddingClick: (wedding: WeddingOut) => void;
  onEditClick: (wedding: WeddingOut) => void;
  onDeleteClick: (wedding: WeddingOut) => void;
}

export const WeddingsTable = memo(function WeddingsTable({
  weddings,
  pageSize,
  onWeddingClick,
  onEditClick,
  onDeleteClick,
}: WeddingsTableProps) {
  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow className="border-b bg-muted/30 hover:bg-muted/30 dark:bg-zinc-900/50">
            <TableHead className="py-4 px-6 text-xs font-semibold text-muted-foreground uppercase tracking-wider h-auto">
              Noivos
            </TableHead>
            <TableHead className="py-4 px-6 text-xs font-semibold text-muted-foreground uppercase tracking-wider h-auto">
              Data do Evento
            </TableHead>
            <TableHead className="py-4 px-6 text-xs font-semibold text-muted-foreground uppercase tracking-wider h-auto">
              Status
            </TableHead>
            <TableHead className="py-4 px-6 text-xs font-semibold text-muted-foreground uppercase tracking-wider h-auto">
              Convidados
            </TableHead>
            <TableHead className="py-4 px-6 text-xs font-semibold text-muted-foreground uppercase tracking-wider h-auto text-right">
              Orçamento
            </TableHead>
            <TableHead className="py-4 px-6 text-xs font-semibold text-muted-foreground uppercase tracking-wider h-auto text-right">
              Pendências
            </TableHead>
            <TableHead className="py-4 px-6 text-xs font-semibold text-muted-foreground uppercase tracking-wider h-auto text-right">
              Ações
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {weddings.map((wedding) => {
            const initials = getWeddingInitials(
              wedding.groom_name,
              wedding.bride_name,
            );
            const badgeStyle = getWeddingStatusBadgeStyle(wedding.status);
            const avatarStyle = getWeddingAvatarStyle(wedding.status);
            const isCompleted = wedding.status === WeddingStatusEnum.COMPLETED;

            return (
              <TableRow
                key={wedding.uuid}
                className="table-row-hover group cursor-pointer"
                onClick={() => onWeddingClick(wedding)}
              >
                <TableCell className="py-4 px-6">
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        "flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border",
                        avatarStyle.bg,
                        avatarStyle.border,
                      )}
                    >
                      <span
                        className={cn(
                          "text-sm font-semibold font-display",
                          avatarStyle.text,
                        )}
                      >
                        {initials}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-foreground">
                        {wedding.groom_name} & {wedding.bride_name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {wedding.location}
                      </p>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="py-4 px-6">
                  <div
                    className={cn(
                      "flex items-center text-sm",
                      isCompleted
                        ? "text-muted-foreground line-through"
                        : "text-foreground",
                    )}
                  >
                    <Calendar className="w-4 h-4 mr-2 text-muted-foreground" />
                    {formatDateBR(wedding.date, {
                      day: "2-digit",
                      month: "short",
                      year: "numeric",
                    })}
                  </div>
                </TableCell>
                <TableCell className="py-4 px-6">
                  <span
                    className={cn(
                      "inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border",
                      badgeStyle.className,
                    )}
                  >
                    {badgeStyle.icon === "check" ? (
                      <Check className="w-3 h-3 mr-1" />
                    ) : (
                      <span
                        className={cn(
                          "w-1.5 h-1.5 rounded-full mr-1.5",
                          badgeStyle.dotClassName,
                        )}
                      />
                    )}
                    {getWeddingStatusLabel(wedding.status)}
                  </span>
                </TableCell>
                <TableCell className="py-4 px-6">
                  {wedding.expected_guests ?? (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell className="py-4 px-6 text-right">
                  {wedding.total_budget != null ? (
                    <span className="font-mono text-sm font-medium text-foreground">
                      {formatCurrencyBRCompact(wedding.total_budget)}
                    </span>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell className="py-4 px-6 text-right">
                  {(() => {
                    const pending =
                      (wedding.overdue_installments ?? 0) +
                      (wedding.incomplete_tasks ?? 0);
                    if (pending === 0) {
                      return (
                        <span className="text-sm text-muted-foreground">
                          —
                        </span>
                      );
                    }
                    return (
                      <span className="inline-flex items-center gap-1 text-sm font-medium text-amber-600 dark:text-amber-400">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        {pending}
                      </span>
                    );
                  })()}
                </TableCell>
                <TableCell
                  className="py-4 px-6 text-right"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-center justify-end gap-2">
                    {isCompleted ? (
                      <button
                        className="p-1.5 text-muted-foreground hover:text-primary rounded-md hover:bg-accent btn-transition"
                        title="Ver Detalhes"
                        onClick={() => onWeddingClick(wedding)}
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    ) : (
                      <>
                        <button
                          className="p-1.5 text-muted-foreground hover:text-primary rounded-md hover:bg-accent btn-transition"
                          title="Editar"
                          onClick={() => onEditClick(wedding)}
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          className="p-1.5 text-muted-foreground hover:text-destructive rounded-md hover:bg-destructive/10 btn-transition"
                          title="Excluir"
                          onClick={() => onDeleteClick(wedding)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
          {weddings.length < pageSize &&
            Array.from({ length: pageSize - weddings.length }).map(
              (_, i) => (
                <TableRow key={`empty-${i}`} aria-hidden>
                  <TableCell className="py-4 px-6" colSpan={7}>
                    &nbsp;
                  </TableCell>
                </TableRow>
              ),
            )}
        </TableBody>
      </Table>
    </div>
  );
});
