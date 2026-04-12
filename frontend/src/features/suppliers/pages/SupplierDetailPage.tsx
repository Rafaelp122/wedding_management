import { Link, useParams } from "react-router-dom";
import { useLogisticsSuppliersRead } from "@/api/generated/v1/endpoints/logistics/logistics";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDateBR } from "@/features/shared/utils/formatters";
import { AlertCircle, ArrowLeft } from "lucide-react";

export default function SupplierDetailPage() {
  const { uuid } = useParams<{ uuid: string }>();

  const { data: response, isLoading, error } = useLogisticsSuppliersRead(uuid!);

  const supplier = response?.data;

  if (isLoading) {
    return (
      <div className="container mx-auto py-6 space-y-4">
        <Skeleton className="h-8 w-56" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-6 space-y-4">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erro ao carregar fornecedor</AlertTitle>
          <AlertDescription>
            {error.message || "Não foi possível carregar os dados do fornecedor."}
          </AlertDescription>
        </Alert>

        <Button asChild variant="outline">
          <Link to="/suppliers">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar para lista
          </Link>
        </Button>
      </div>
    );
  }

  if (!supplier) {
    return (
      <div className="container mx-auto py-6 space-y-4">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Fornecedor não encontrado</AlertTitle>
          <AlertDescription>
            O fornecedor solicitado não foi encontrado ou você não tem permissão para acessá-lo.
          </AlertDescription>
        </Alert>

        <Button asChild variant="outline">
          <Link to="/suppliers">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar para lista
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <Button asChild variant="outline" size="sm">
        <Link to="/suppliers">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Voltar para lista
        </Link>
      </Button>

      <Card>
        <CardHeader>
          <CardTitle>{supplier.name}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            <strong>Status:</strong> {supplier.is_active ? "Ativo" : "Inativo"}
          </p>
          <p>
            <strong>E-mail:</strong> {supplier.email || "—"}
          </p>
          <p>
            <strong>Telefone:</strong> {supplier.phone || "—"}
          </p>
          <p>
            <strong>CNPJ:</strong> {supplier.cnpj || "—"}
          </p>
          <p>
            <strong>Cadastrado em:</strong> {formatDateBR(supplier.created_at)}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
