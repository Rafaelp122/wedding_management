import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search } from "lucide-react";

interface WeddingFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  statusFilter: string;
  onStatusFilterChange: (value: string) => void;
}

export function WeddingFilters({
  search,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
}: WeddingFiltersProps) {
  return (
    <div className="flex flex-col gap-4 md:flex-row md:items-center">
      {/* Busca */}
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Buscar por nome dos noivos ou local..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Filtro de Status */}
      <Select value={statusFilter} onValueChange={onStatusFilterChange}>
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
