import React from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export interface PageFilterBarProps extends React.HTMLAttributes<HTMLDivElement> {
  search?: string;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;
  children?: React.ReactNode;
}

export function PageFilterBar({
  search,
  onSearchChange,
  searchPlaceholder = "Buscar...",
  children,
  className,
  ...props
}: PageFilterBarProps) {
  return (
    <div
      className={cn(
        "flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between",
        className,
      )}
      {...props}
    >
      {onSearchChange !== undefined && (
        <div className="relative flex-1 sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder={searchPlaceholder}
            aria-label={searchPlaceholder || "Buscar"}
            value={search ?? ""}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9"
          />
        </div>
      )}

      {children && (
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {children}
        </div>
      )}
    </div>
  );
}
