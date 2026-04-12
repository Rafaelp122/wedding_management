import {
  Calendar,
  DollarSign,
  FileText,
  ListChecks,
  Package,
  Receipt,
  Users,
  type LucideIcon,
} from "lucide-react";

import type { WeddingOut } from "@/api/generated/v1/models";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { WeddingBudget } from "./WeddingBudget";
import { WeddingOverview } from "./WeddingOverview";
import { WeddingVendorsItemsTab } from "./WeddingVendorsItemsTab";
import { WeddingExpensesTab } from "./WeddingExpensesTab";
import { WeddingTimelineTab } from "./WeddingTimelineTab";
import { WeddingChecklistTab } from "./WeddingChecklistTab";

interface WeddingDetailTabsProps {
  wedding: WeddingOut;
}

interface PlaceholderTabAlertProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

function PlaceholderTabAlert({
  icon: Icon,
  title,
  description,
}: PlaceholderTabAlertProps) {
  return (
    <Alert>
      <Icon className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{description}</AlertDescription>
    </Alert>
  );
}

export function WeddingDetailTabs({ wedding }: WeddingDetailTabsProps) {
  return (
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
        <WeddingVendorsItemsTab weddingUuid={wedding.uuid} />
      </TabsContent>

      <TabsContent value="expenses" className="space-y-4">
        <WeddingExpensesTab weddingUuid={wedding.uuid} />
      </TabsContent>

      <TabsContent value="timeline" className="space-y-4">
        <WeddingTimelineTab weddingUuid={wedding.uuid} />
      </TabsContent>

      <TabsContent value="checklist" className="space-y-4">
        <WeddingChecklistTab weddingUuid={wedding.uuid} />
      </TabsContent>

      <TabsContent value="guests" className="space-y-4">
        <PlaceholderTabAlert
          icon={Users}
          title="Em breve"
          description="A gestão de convidados será disponibilizada nesta aba."
        />
      </TabsContent>
    </Tabs>
  );
}
