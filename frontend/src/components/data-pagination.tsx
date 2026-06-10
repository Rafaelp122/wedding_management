import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface DataPaginationProps {
  from: number;
  to: number;
  totalCount: number;
  totalPages: number;
  currentPage: number;
  hasPrevious: boolean;
  hasNext: boolean;
  isFetching?: boolean;
  onPrevious: () => void;
  onNext: () => void;
  onGoToPage: (page: number) => void;
}

export function DataPagination({
  from,
  to,
  totalCount,
  totalPages,
  currentPage,
  hasPrevious,
  hasNext,
  isFetching,
  onPrevious,
  onNext,
  onGoToPage,
}: DataPaginationProps) {
  if (totalCount === 0) return null;

  const singlePage = totalPages <= 1;

  const safeTotalPages = Number.isFinite(totalPages)
    ? Math.min(totalPages, 20)
    : 1;
  const pages = Array.from({ length: safeTotalPages }, (_, i) => i + 1);

  return (
    <div className="px-6 py-4 border-t bg-muted/30 flex items-center justify-between">
      <span className="text-sm text-muted-foreground">
        Mostrando{" "}
        {singlePage ? (
          <>
            <span className="font-medium text-foreground">{totalCount}</span>{" "}
            de{" "}
            <span className="font-medium text-foreground">{totalCount}</span>
          </>
        ) : (
          <>
            <span className="font-medium text-foreground">{from}</span> a{" "}
            <span className="font-medium text-foreground">{to}</span> de{" "}
            <span className="font-medium text-foreground">{totalCount}</span>
          </>
        )}{" "}
        resultado{totalCount !== 1 ? "s" : ""}
      </span>
      {!singlePage && (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            disabled={!hasPrevious || isFetching}
            onClick={onPrevious}
          >
            <ChevronLeft className="size-4" />
            <span className="sr-only">Anterior</span>
          </Button>
          {pages.map((page) => (
            <Button
              key={page}
              variant={page === currentPage ? "default" : "ghost"}
              size="icon"
              className={cn(
                "h-8 w-8 text-sm font-medium",
                page !== currentPage &&
                  "text-muted-foreground hover:text-foreground",
              )}
              disabled={isFetching}
              onClick={() => onGoToPage(page)}
            >
              {page}
            </Button>
          ))}
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            disabled={!hasNext || isFetching}
            onClick={onNext}
          >
            <span className="sr-only">Próximo</span>
            <ChevronRight className="size-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
