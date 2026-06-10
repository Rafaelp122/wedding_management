import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search } from "lucide-react";
import type { WeddingStatusFilter } from "@/features/weddings/utils/wedding-status";

interface WeddingFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  statusFilter: WeddingStatusFilter;
  onStatusFilterChange: (value: WeddingStatusFilter) => void;
}

export function WeddingFilters({
  search,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
}: WeddingFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 items-center justify-between bg-card p-2 rounded-xl border shadow-sm">
      <div className="flex flex-1 w-full sm:w-auto gap-2">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por noivos ou local..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9 border-0 bg-muted/50 focus-visible:ring-2 focus-visible:ring-ring/50"
          />
        </div>

        <Select
          value={statusFilter}
          onValueChange={(value) =>
            onStatusFilterChange(value as WeddingStatusFilter)
          }
        >
          <SelectTrigger className="w-full sm:w-48 border-0 bg-muted/50 focus:ring-2 focus:ring-ring/50">
            <SelectValue placeholder="Todos os Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos os Status</SelectItem>
            <SelectItem value="IN_PROGRESS">Em Andamento</SelectItem>
            <SelectItem value="COMPLETED">Concluído</SelectItem>
            <SelectItem value="CANCELED">Cancelado</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
