import { useMemo, useState } from "react";
import { toast } from "sonner";
import {
  useLogisticsSuppliersCreate,
  useLogisticsSuppliersDelete,
  useLogisticsSuppliersList,
  useLogisticsSuppliersPartialUpdate,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import type { SupplierOut } from "@/api/generated/v1/models";
import { getApiErrorInfo } from "@/api/error-utils";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  AlertCircle,
  Edit,
  MoreHorizontal,
  Plus,
  Search,
  Trash2,
} from "lucide-react";

interface SupplierFormState {
  uuid?: string;
  name: string;
  cnpj: string;
  phone: string;
  email: string;
  status: "active" | "inactive";
}

const emptyFormState: SupplierFormState = {
  name: "",
  cnpj: "",
  phone: "",
  email: "",
  status: "active",
};

const formatDate = (value: string): string => {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleDateString("pt-BR");
};

export default function SuppliersPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "inactive">(
    "all",
  );
  const [formOpen, setFormOpen] = useState(false);
  const [formMode, setFormMode] = useState<"create" | "edit">("create");
  const [formState, setFormState] = useState<SupplierFormState>(emptyFormState);
  const [supplierToDelete, setSupplierToDelete] = useState<SupplierOut | null>(null);

  const {
    data: suppliersResponse,
    isLoading,
    error,
    refetch,
  } = useLogisticsSuppliersList({ limit: 300 });
  const createSupplierMutation = useLogisticsSuppliersCreate();
  const updateSupplierMutation = useLogisticsSuppliersPartialUpdate();
  const deleteSupplierMutation = useLogisticsSuppliersDelete();

  const suppliers = useMemo(
    () => suppliersResponse?.data.items ?? [],
    [suppliersResponse],
  );
  const totalCount = suppliersResponse?.data.count ?? 0;

  const filteredSuppliers = useMemo(() => {
    return suppliers.filter((supplier) => {
      const matchesSearch =
        search === "" ||
        supplier.name.toLowerCase().includes(search.toLowerCase()) ||
        supplier.email.toLowerCase().includes(search.toLowerCase()) ||
        supplier.phone.toLowerCase().includes(search.toLowerCase()) ||
        supplier.cnpj.toLowerCase().includes(search.toLowerCase());

      const matchesStatus =
        statusFilter === "all" ||
        (statusFilter === "active" && supplier.is_active) ||
        (statusFilter === "inactive" && !supplier.is_active);

      return matchesSearch && matchesStatus;
    });
  }, [suppliers, search, statusFilter]);

  const openCreateDialog = () => {
    setFormMode("create");
    setFormState(emptyFormState);
    setFormOpen(true);
  };

  const openEditDialog = (supplier: SupplierOut) => {
    setFormMode("edit");
    setFormState({
      uuid: supplier.uuid,
      name: supplier.name,
      cnpj: supplier.cnpj,
      phone: supplier.phone,
      email: supplier.email,
      status: supplier.is_active ? "active" : "inactive",
    });
    setFormOpen(true);
  };

  const handleSaveSupplier = async () => {
    if (!formState.name.trim()) {
      toast.error("Informe o nome do fornecedor.");
      return;
    }

    if (!formState.email.trim()) {
      toast.error("Informe o e-mail do fornecedor.");
      return;
    }

    if (!formState.phone.trim()) {
      toast.error("Informe o telefone do fornecedor.");
      return;
    }

    if (!formState.cnpj.trim()) {
      toast.error("Informe o CNPJ do fornecedor.");
      return;
    }

    const payload = {
      name: formState.name.trim(),
      cnpj: formState.cnpj.trim(),
      phone: formState.phone.trim(),
      email: formState.email.trim(),
      is_active: formState.status === "active",
    };

    try {
      if (formMode === "create") {
        await createSupplierMutation.mutateAsync({ data: payload });
        toast.success("Fornecedor criado com sucesso!");
      } else {
        if (!formState.uuid) {
          toast.error("Fornecedor inválido para edição.");
          return;
        }

        await updateSupplierMutation.mutateAsync({
          uuid: formState.uuid,
          data: payload,
        });
        toast.success("Fornecedor atualizado com sucesso!");
      }

      setFormOpen(false);
      await refetch();
    } catch (mutationError) {
      const { message } = getApiErrorInfo(
        mutationError,
        "Não foi possível salvar o fornecedor.",
      );
      toast.error(message);
    }
  };

  const handleDeleteSupplier = async () => {
    if (!supplierToDelete) return;

    try {
      await deleteSupplierMutation.mutateAsync({ uuid: supplierToDelete.uuid });
      toast.success("Fornecedor removido com sucesso!");
      setSupplierToDelete(null);
      await refetch();
    } catch (mutationError) {
      const { message } = getApiErrorInfo(
        mutationError,
        "Não foi possível remover o fornecedor.",
      );
      toast.error(message);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (error) {
    const { message } = getApiErrorInfo(
      error,
      "Não foi possível carregar a lista de fornecedores.",
    );

    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erro ao carregar dados</AlertTitle>
        <AlertDescription>
          {message}
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            className="mt-4"
          >
            Tentar Novamente
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Fornecedores</h2>
          <p className="text-muted-foreground">
            Gerencie o cadastro global de fornecedores da sua operação.
          </p>
        </div>
        <Button onClick={openCreateDialog}>
          <Plus className="mr-2 h-4 w-4" />
          Novo Fornecedor
        </Button>
      </div>

      <div className="flex flex-col gap-4 md:flex-row md:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por nome, e-mail, telefone ou CNPJ..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="pl-9"
          />
        </div>

        <Select
          value={statusFilter}
          onValueChange={(value: "all" | "active" | "inactive") =>
            setStatusFilter(value)
          }
        >
          <SelectTrigger className="w-full md:w-50">
            <SelectValue placeholder="Filtrar por status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos os status</SelectItem>
            <SelectItem value="active">Ativos</SelectItem>
            <SelectItem value="inactive">Inativos</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            {filteredSuppliers.length} de {totalCount} fornecedores
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredSuppliers.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle className="mb-4 h-12 w-12 text-muted-foreground" />
              <h3 className="text-lg font-semibold">Nenhum fornecedor encontrado</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {search || statusFilter !== "all"
                  ? "Tente ajustar os filtros de busca"
                  : "Clique em 'Novo Fornecedor' para começar"}
              </p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Fornecedor</TableHead>
                    <TableHead>E-mail</TableHead>
                    <TableHead>Telefone</TableHead>
                    <TableHead>CNPJ</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Cadastrado em</TableHead>
                    <TableHead className="w-20">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredSuppliers.map((supplier) => (
                    <TableRow key={supplier.uuid}>
                      <TableCell className="font-medium">{supplier.name}</TableCell>
                      <TableCell>{supplier.email || "—"}</TableCell>
                      <TableCell>{supplier.phone || "—"}</TableCell>
                      <TableCell>{supplier.cnpj || "—"}</TableCell>
                      <TableCell>
                        <Badge variant={supplier.is_active ? "secondary" : "outline"}>
                          {supplier.is_active ? "Ativo" : "Inativo"}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatDate(supplier.created_at)}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="h-4 w-4" />
                              <span className="sr-only">Abrir menu</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>Ações</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => openEditDialog(supplier)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Editar
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-destructive focus:text-destructive"
                              onClick={() => setSupplierToDelete(supplier)}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Deletar
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {formMode === "create" ? "Novo fornecedor" : "Editar fornecedor"}
            </DialogTitle>
            <DialogDescription>
              Preencha os dados principais para manter o cadastro de fornecedores.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="supplier-name">Nome</Label>
              <Input
                id="supplier-name"
                value={formState.name}
                onChange={(event) =>
                  setFormState((current) => ({
                    ...current,
                    name: event.target.value,
                  }))
                }
                placeholder="Nome do fornecedor"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="supplier-email">E-mail</Label>
                <Input
                  id="supplier-email"
                  type="email"
                  value={formState.email}
                  onChange={(event) =>
                    setFormState((current) => ({
                      ...current,
                      email: event.target.value,
                    }))
                  }
                  placeholder="contato@fornecedor.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="supplier-phone">Telefone</Label>
                <Input
                  id="supplier-phone"
                  value={formState.phone}
                  onChange={(event) =>
                    setFormState((current) => ({
                      ...current,
                      phone: event.target.value,
                    }))
                  }
                  placeholder="(21) 99999-9999"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="supplier-cnpj">CNPJ</Label>
                <Input
                  id="supplier-cnpj"
                  value={formState.cnpj}
                  onChange={(event) =>
                    setFormState((current) => ({
                      ...current,
                      cnpj: event.target.value,
                    }))
                  }
                  placeholder="00.000.000/0000-00"
                />
              </div>

              <div className="space-y-2">
                <Label>Status</Label>
                <Select
                  value={formState.status}
                  onValueChange={(value: "active" | "inactive") =>
                    setFormState((current) => ({
                      ...current,
                      status: value,
                    }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Ativo</SelectItem>
                    <SelectItem value="inactive">Inativo</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setFormOpen(false)}>
              Cancelar
            </Button>
            <Button
              onClick={handleSaveSupplier}
              disabled={
                createSupplierMutation.isPending || updateSupplierMutation.isPending
              }
            >
              {createSupplierMutation.isPending || updateSupplierMutation.isPending
                ? "Salvando..."
                : "Salvar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={!!supplierToDelete}
        onOpenChange={(open) => !open && setSupplierToDelete(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Excluir fornecedor</DialogTitle>
            <DialogDescription>
              Esta ação não pode ser desfeita.
            </DialogDescription>
          </DialogHeader>

          <p className="text-sm text-muted-foreground">
            Deseja realmente excluir{" "}
            <span className="font-semibold text-foreground">
              {supplierToDelete?.name}
            </span>
            ?
          </p>

          <DialogFooter>
            <Button variant="outline" onClick={() => setSupplierToDelete(null)}>
              Cancelar
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteSupplier}
              disabled={deleteSupplierMutation.isPending}
            >
              {deleteSupplierMutation.isPending ? "Excluindo..." : "Excluir"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
