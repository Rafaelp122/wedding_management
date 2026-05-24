import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";

interface DataPaginationProps {
  from: number;
  to: number;
  totalCount: number;
  hasPrevious: boolean;
  hasNext: boolean;
  isFetching?: boolean;
  onPrevious: () => void;
  onNext: () => void;
}

export function DataPagination({
  from,
  to,
  totalCount,
  hasPrevious,
  hasNext,
  isFetching,
  onPrevious,
  onNext,
}: DataPaginationProps) {
  return (
    <div className="flex items-center justify-between gap-4 pt-4">
      <span className="text-sm text-muted-foreground">
        Mostrando {from}–{to} de {totalCount} resultado
        {totalCount !== 1 ? "s" : ""}
      </span>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={!hasPrevious || isFetching}
          onClick={onPrevious}
        >
          <ChevronLeft className="size-4" />
          <span className="sr-only">Anterior</span>
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!hasNext || isFetching}
          onClick={onNext}
        >
          <span className="sr-only">Próximo</span>
          <ChevronRight className="size-4" />
        </Button>
      </div>
    </div>
  );
}
