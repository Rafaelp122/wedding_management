import { memo } from "react";
import type { ClientOut } from "@/api/generated/v1/models/clientOut";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { formatDateBR } from "@/lib/formatters";
import { Pencil, Trash2, Users, Mail, Phone } from "lucide-react";

interface ClientsTableProps {
  clients: ClientOut[];
  onEditClient: (client: ClientOut) => void;
  onDeleteClient: (client: ClientOut) => void;
  isDeleting?: boolean;
}

/**
 * Componente de apresentação (Dumb) para tabela de clientes (ADR-024).
 */
export const ClientsTable = memo(function ClientsTable({
  clients,
  onEditClient,
  onDeleteClient,
  isDeleting = false,
}: ClientsTableProps) {
  if (clients.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 border border-dashed rounded-lg bg-card/50 text-center">
        <Users className="h-10 w-10 text-muted-foreground/40 mb-3" />
        <h3 className="text-sm font-semibold text-foreground">
          Nenhum cliente cadastrado
        </h3>
        <p className="text-xs text-muted-foreground mt-1 max-w-sm">
          Cadastre novos noivos, parentes e contratantes financeiros para vincular aos casamentos e contratos da sua assessoria.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-md border bg-card overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Nome</TableHead>
            <TableHead>CPF</TableHead>
            <TableHead>Contatos</TableHead>
            <TableHead>Observações</TableHead>
            <TableHead>Cadastrado em</TableHead>
            <TableHead className="text-right">Ações</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {clients.map((client) => (
            <TableRow key={client.uuid} data-testid={`client-row-${client.uuid}`}>
              <TableCell className="font-medium text-foreground">
                {client.name}
              </TableCell>
              <TableCell className="text-muted-foreground text-xs">
                {client.cpf || "—"}
              </TableCell>
              <TableCell>
                <div className="flex flex-col gap-0.5 text-xs text-muted-foreground">
                  {client.email && (
                    <div className="flex items-center gap-1.5">
                      <Mail className="h-3 w-3 shrink-0 text-muted-foreground/70" />
                      <span className="truncate max-w-[200px]">{client.email}</span>
                    </div>
                  )}
                  {client.phone && (
                    <div className="flex items-center gap-1.5">
                      <Phone className="h-3 w-3 shrink-0 text-muted-foreground/70" />
                      <span>{client.phone}</span>
                    </div>
                  )}
                  {!client.email && !client.phone && "—"}
                </div>
              </TableCell>
              <TableCell className="text-xs text-muted-foreground max-w-[250px] truncate">
                {client.notes || "—"}
              </TableCell>
              <TableCell className="text-xs text-muted-foreground">
                {formatDateBR(client.created_at, {
                  day: "2-digit",
                  month: "2-digit",
                  year: "numeric",
                })}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    onClick={() => onEditClient(client)}
                    aria-label={`Editar ${client.name}`}
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-destructive"
                    onClick={() => onDeleteClient(client)}
                    disabled={isDeleting}
                    aria-label={`Excluir ${client.name}`}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
});
