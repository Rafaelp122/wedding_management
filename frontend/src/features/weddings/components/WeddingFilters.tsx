import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search } from "lucide-react";
import type { WeddingStatusFilter } from "../utils/weddingStatus";

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
    <div className="flex flex-col md:flex-row md:items-center gap-4">
      {/* Busca */}
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
        <Input
          placeholder="Buscar por nome dos noivos ou local..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Filtro de Status */}
      <Select value={statusFilter} onValueChange={(value) => onStatusFilterChange(value as WeddingStatusFilter)}>
        <SelectTrigger className="w-full md:w-50">
          <SelectValue placeholder="Filtrar por status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Todos os status</SelectItem>
          <SelectItem value="IN_PROGRESS">Em Andamento</SelectItem>
          <SelectItem value="COMPLETED">Concluído</SelectItem>
          <SelectItem value="CANCELED">Cancelado</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
