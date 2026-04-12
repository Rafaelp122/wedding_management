import { AlertCircle, FileText, Package } from "lucide-react";

import { useWeddingVendorsItems } from "../hooks/useWeddingVendorsItems";
import { WeddingVendorsTable } from "./WeddingVendorsTable";
import { WeddingItemsTable } from "./WeddingItemsTable";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface WeddingVendorsItemsTabProps {
  weddingUuid: string;
}

export function WeddingVendorsItemsTab({ weddingUuid }: WeddingVendorsItemsTabProps) {
  const { contracts, items, isLoading, error } = useWeddingVendorsItems(weddingUuid);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-[300px] w-full rounded-md" />
        <Skeleton className="h-[300px] w-full rounded-md" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Não foi possível carregar os dados de logística e fornecedores.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Contratos de Fornecedores */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Contratos de Fornecedores
          </CardTitle>
          <CardDescription>
            Fornecedores e serviços vinculados formalmente a este evento.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <WeddingVendorsTable contracts={contracts} />
        </CardContent>
      </Card>

      {/* Itens Logísticos */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5 text-primary" />
            Itens Logísticos
          </CardTitle>
          <CardDescription>
            Acompanhamento de recursos materiais, brindes e infraestrutura.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <WeddingItemsTable items={items} />
        </CardContent>
      </Card>
    </div>
  );
}
