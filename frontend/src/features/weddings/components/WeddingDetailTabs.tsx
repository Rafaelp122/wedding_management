import {
  Calendar,
  ClipboardList,
  LayoutDashboard,
  ListChecks,
  Package,
  Wallet,
} from "lucide-react";
import { useSearchParams } from "react-router-dom";

import type { WeddingOut } from "@/api/generated/v1/models";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { WeddingFinancesView } from "./WeddingFinancesView";
import { WeddingOverview } from "./WeddingOverview";
import { WeddingVendorsItemsTab } from "./WeddingVendorsItemsTab";
import { WeddingTimelineTab } from "./WeddingTimelineTab";
import { WeddingChecklistTab } from "./WeddingChecklistTab";

interface WeddingDetailTabsProps {
  wedding: WeddingOut;
}

export function WeddingDetailTabs({ wedding }: WeddingDetailTabsProps) {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get("tab") || "general";

  const handleTabChange = (value: string) => {
    setSearchParams((prev) => {
      prev.set("tab", value);
      return prev;
    }, { replace: true });
  };

  const activeSubTab = searchParams.get("subtab") || "timeline";
  const handleSubTabChange = (value: string) => {
    setSearchParams((prev) => {
      prev.set("subtab", value);
      return prev;
    }, { replace: true });
  };

  return (
    <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-4">
      <TabsList className="w-full justify-start overflow-x-auto border-b bg-transparent p-0">
        <TabsTrigger
          value="general"
          className="relative h-9 rounded-none border-b-2 border-b-transparent bg-transparent px-4 pb-3 pt-2 font-semibold text-muted-foreground shadow-none transition-none data-[state=active]:border-b-primary data-[state=active]:text-foreground data-[state=active]:shadow-none"
        >
          <LayoutDashboard className="mr-2 h-4 w-4" />
          Geral
        </TabsTrigger>
        <TabsTrigger
          value="finances"
          className="relative h-9 rounded-none border-b-2 border-b-transparent bg-transparent px-4 pb-3 pt-2 font-semibold text-muted-foreground shadow-none transition-none data-[state=active]:border-b-primary data-[state=active]:text-foreground data-[state=active]:shadow-none"
        >
          <Wallet className="mr-2 h-4 w-4" />
          Finanças
        </TabsTrigger>
        <TabsTrigger
          value="logistics"
          className="relative h-9 rounded-none border-b-2 border-b-transparent bg-transparent px-4 pb-3 pt-2 font-semibold text-muted-foreground shadow-none transition-none data-[state=active]:border-b-primary data-[state=active]:text-foreground data-[state=active]:shadow-none"
        >
          <Package className="mr-2 h-4 w-4" />
          Logística
        </TabsTrigger>
        <TabsTrigger
          value="planning"
          className="relative h-9 rounded-none border-b-2 border-b-transparent bg-transparent px-4 pb-3 pt-2 font-semibold text-muted-foreground shadow-none transition-none data-[state=active]:border-b-primary data-[state=active]:text-foreground data-[state=active]:shadow-none"
        >
          <ClipboardList className="mr-2 h-4 w-4" />
          Planejamento
        </TabsTrigger>
      </TabsList>

      <TabsContent value="general" className="space-y-4 pt-4">
        <WeddingOverview wedding={wedding} />
      </TabsContent>

      <TabsContent value="finances" className="space-y-4 pt-4">
        <WeddingFinancesView weddingUuid={wedding.uuid} />
      </TabsContent>

      <TabsContent value="logistics" className="space-y-4 pt-4">
        <WeddingVendorsItemsTab weddingUuid={wedding.uuid} />
      </TabsContent>

      <TabsContent value="planning" className="space-y-4 pt-4">
        <Tabs value={activeSubTab} onValueChange={handleSubTabChange} className="space-y-4">
          <TabsList>
            <TabsTrigger value="timeline" className="gap-2">
              <Calendar className="h-4 w-4" />
              Cronograma
            </TabsTrigger>
            <TabsTrigger value="checklist" className="gap-2">
              <ListChecks className="h-4 w-4" />
              Checklist
            </TabsTrigger>
          </TabsList>
          <TabsContent value="timeline">
            <WeddingTimelineTab weddingUuid={wedding.uuid} />
          </TabsContent>
          <TabsContent value="checklist">
            <WeddingChecklistTab weddingUuid={wedding.uuid} />
          </TabsContent>
        </Tabs>
      </TabsContent>
    </Tabs>
  );
}
