import { useParams, Link } from "react-router-dom";
import { useWeddingsRead } from "@/api/generated/v1/endpoints/weddings/weddings";
import { WeddingOverview } from "@/features/weddings/components/WeddingOverview";
import { WeddingBudget } from "@/features/weddings/components/WeddingBudget";

import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  ArrowLeft,
  AlertCircle,
  DollarSign,
  Calendar,
  Users,
  FileText,
  Package,
  Receipt,
  ListChecks,
} from "lucide-react";

export default function WeddingDetailPage() {
  const { uuid } = useParams<{ uuid: string }>();

  const { data: response, isLoading, error } = useWeddingsRead(uuid!);

  const wedding = response?.data;

  if (isLoading) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-[400px] w-full" />
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
            {error.message || "Não foi possível carregar os dados do casamento."}
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

  if (!wedding) {
    return (
      <div className="container mx-auto py-6">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Casamento não encontrado</AlertTitle>
          <AlertDescription>
            O casamento solicitado não foi encontrado ou você não tem permissão para acessá-lo.
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
    <div className="container mx-auto py-6 space-y-6">
      {/* Breadcrumb */}
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to="/dashboard">Dashboard</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to="/weddings">Casamentos</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>
              {wedding.groom_name} & {wedding.bride_name}
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Botão voltar */}
      <div>
        <Button asChild variant="outline" size="sm">
          <Link to="/weddings">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Voltar para lista
          </Link>
        </Button>
      </div>

      {/* Tabs de conteúdo */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="w-full justify-start overflow-x-auto">
          <TabsTrigger value="overview" className="gap-2 whitespace-nowrap">
            <FileText className="h-4 w-4" />
            Visão Geral
          </TabsTrigger>
          <TabsTrigger value="budget" className="gap-2 whitespace-nowrap">
            <DollarSign className="h-4 w-4" />
            Orçamento
          </TabsTrigger>
          <TabsTrigger value="vendors-items" className="gap-2 whitespace-nowrap">
            <Package className="h-4 w-4" />
            Fornecedores/Itens
          </TabsTrigger>
          <TabsTrigger value="expenses" className="gap-2 whitespace-nowrap">
            <Receipt className="h-4 w-4" />
            Despesas
          </TabsTrigger>
          <TabsTrigger value="timeline" className="gap-2 whitespace-nowrap">
            <Calendar className="h-4 w-4" />
            Cronograma
          </TabsTrigger>
          <TabsTrigger value="checklist" className="gap-2 whitespace-nowrap">
            <ListChecks className="h-4 w-4" />
            Checklist
          </TabsTrigger>
          <TabsTrigger value="guests" className="gap-2 whitespace-nowrap">
            <Users className="h-4 w-4" />
            Convidados
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <WeddingOverview wedding={wedding} />
        </TabsContent>

        <TabsContent value="budget" className="space-y-4">
          <WeddingBudget weddingUuid={wedding.uuid} />
        </TabsContent>

        <TabsContent value="vendors-items" className="space-y-4">
          <Alert>
            <Package className="h-4 w-4" />
            <AlertTitle>Fornecedores e itens deste casamento</AlertTitle>
            <AlertDescription>
              Aqui ficará o workspace operacional para vincular fornecedores, contratos e
              itens diretamente a este casamento.
            </AlertDescription>
          </Alert>
        </TabsContent>

        <TabsContent value="expenses" className="space-y-4">
          <Alert>
            <Receipt className="h-4 w-4" />
            <AlertTitle>Despesas do casamento</AlertTitle>
            <AlertDescription>
              Esta aba concentrará despesas e parcelas vinculadas ao evento selecionado.
            </AlertDescription>
          </Alert>
        </TabsContent>

        <TabsContent value="timeline" className="space-y-4">
          <Alert>
            <Calendar className="h-4 w-4" />
            <AlertTitle>Em breve</AlertTitle>
            <AlertDescription>
              O cronograma específico deste casamento será exibido aqui.
            </AlertDescription>
          </Alert>
        </TabsContent>

        <TabsContent value="checklist" className="space-y-4">
          <Alert>
            <ListChecks className="h-4 w-4" />
            <AlertTitle>Em breve</AlertTitle>
            <AlertDescription>
              O checklist personalizado de tarefas do casamento será disponibilizado aqui.
            </AlertDescription>
          </Alert>
        </TabsContent>

        <TabsContent value="guests" className="space-y-4">
          <Alert>
            <Users className="h-4 w-4" />
            <AlertTitle>Em breve</AlertTitle>
            <AlertDescription>
              A gestão de convidados será disponibilizada nesta aba.
            </AlertDescription>
          </Alert>
        </TabsContent>
      </Tabs>
    </div>
  );
}
