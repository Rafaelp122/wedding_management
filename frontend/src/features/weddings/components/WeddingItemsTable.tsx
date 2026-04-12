import type { ItemOut } from "@/api/generated/v1/models";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface WeddingItemsTableProps {
  items: ItemOut[];
}

export function WeddingItemsTable({ items }: WeddingItemsTableProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground border rounded-md">
        <p className="text-sm">Nenhum item logístico planejado para este evento.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Item</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead>Quantidade</TableHead>
            <TableHead>Status de Aquisição</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((item) => (
            <TableRow key={item.uuid}>
              <TableCell className="font-medium">{item.name}</TableCell>
              <TableCell className="max-w-[200px] truncate" title={item.description}>
                {item.description || "N/A"}
              </TableCell>
              <TableCell>{item.quantity}</TableCell>
              <TableCell>
                <Badge variant="outline">
                  {item.acquisition_status}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
