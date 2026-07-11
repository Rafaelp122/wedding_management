import { useParams, Link } from "react-router-dom";
import { useWeddingDetail } from "../hooks/useWeddingDetail";
import { WeddingDetailTabs } from "@/features/weddings/components/WeddingDetailTabs";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ArrowLeft, AlertCircle } from "lucide-react";

export default function WeddingDetailPage() {
  const { uuid } = useParams<{ uuid: string }>();

  const { data: response, isLoading, error } = useWeddingDetail(uuid!);

  const wedding = response?.data;

  if (!uuid) {
    return (
      <div className="container mx-auto py-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>URL inválida</AlertTitle>
          <AlertDescription>
            Nenhum UUID de casamento foi encontrado na URL.
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button asChild variant="outline">
            <Link to="/weddings">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Voltar para lista
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erro ao carregar casamento</AlertTitle>
          <AlertDescription>
            {error.message ||
              "Não foi possível carregar os dados do casamento."}
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button asChild variant="outline">
            <Link to="/weddings">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Voltar para lista
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 flex flex-col gap-6">
      {/* Botão voltar */}
      <div>
        <Button asChild variant="outline" size="sm">
          <Link to="/weddings">
            <ArrowLeft className="mr-2 size-4" />
            Voltar para lista
          </Link>
        </Button>
      </div>

      {/* Nome do casal — skeleton enquanto carrega */}
      {isLoading && <Skeleton className="h-8 w-64" />}

      {/* Tabs de conteúdo — skeleton enquanto carrega, tabs reais após */}
      {isLoading ? (
        <Skeleton className="h-12 w-full" />
      ) : wedding ? (
        <WeddingDetailTabs wedding={wedding} />
      ) : (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Casamento não encontrado</AlertTitle>
          <AlertDescription>
            O casamento solicitado não foi encontrado ou você não tem permissão
            para acessá-lo.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
