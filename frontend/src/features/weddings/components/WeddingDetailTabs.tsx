import { lazy, Suspense } from "react";
import {
  Calendar,
  ListChecks,
  LayoutDashboard,
  ClipboardList,
  Wallet,
  Package,
} from "lucide-react";
import { useSearchParams } from "react-router-dom";

import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import type { WeddingDashboardOut } from "@/api/generated/v1/models/weddingDashboardOut";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { WeddingOverview } from "./WeddingOverview";

const WeddingFinancesView = lazy(() =>
  import("@/features/finances/components/FinancesView").then((m) => ({
    default: m.WeddingFinancesView,
  })),
);

const WeddingVendorsItemsTab = lazy(() =>
  import("@/features/logistics/components/VendorsItemsView").then((m) => ({
    default: m.WeddingVendorsItemsTab,
  })),
);

const WeddingTimelineTab = lazy(() =>
  import("@/features/scheduler/components/events/TimelineView").then((m) => ({
    default: m.WeddingTimelineTab,
  })),
);

const WeddingChecklistTab = lazy(() =>
  import("@/features/scheduler/components/tasks/ChecklistView").then((m) => ({
    default: m.WeddingChecklistTab,
  })),
);

interface WeddingDetailTabsProps {
  wedding: WeddingOut;
  overview?: WeddingDashboardOut | null;
}

export function WeddingDetailTabs({ wedding, overview }: WeddingDetailTabsProps) {
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
      <TabsList className="w-full justify-start overflow-x-auto border-b bg-transparent p-0 h-auto gap-8 rounded-none">
        <TabsTrigger
          value="general"
          className="relative rounded-none border-b-2 border-transparent bg-transparent px-0 py-3 text-sm font-medium text-muted-foreground shadow-none transition-all data-[state=active]:border-b-primary data-[state=active]:text-primary data-[state=active]:font-semibold data-[state=active]:shadow-none cursor-pointer flex items-center"
        >
          <LayoutDashboard className="mr-2 h-4 w-4 shrink-0" />
          Visão Geral
        </TabsTrigger>
        <TabsTrigger
          value="planning"
          className="relative rounded-none border-b-2 border-transparent bg-transparent px-0 py-3 text-sm font-medium text-muted-foreground shadow-none transition-all data-[state=active]:border-b-primary data-[state=active]:text-primary data-[state=active]:font-semibold data-[state=active]:shadow-none cursor-pointer flex items-center"
        >
          <ClipboardList className="mr-2 h-4 w-4 shrink-0" />
          Planejamento
        </TabsTrigger>
        <TabsTrigger
          value="finances"
          className="relative rounded-none border-b-2 border-transparent bg-transparent px-0 py-3 text-sm font-medium text-muted-foreground shadow-none transition-all data-[state=active]:border-b-primary data-[state=active]:text-primary data-[state=active]:font-semibold data-[state=active]:shadow-none cursor-pointer flex items-center"
        >
          <Wallet className="mr-2 h-4 w-4 shrink-0" />
          Finanças
        </TabsTrigger>
        <TabsTrigger
          value="logistics"
          className="relative rounded-none border-b-2 border-transparent bg-transparent px-0 py-3 text-sm font-medium text-muted-foreground shadow-none transition-all data-[state=active]:border-b-primary data-[state=active]:text-primary data-[state=active]:font-semibold data-[state=active]:shadow-none cursor-pointer flex items-center"
        >
          <Package className="mr-2 h-4 w-4 shrink-0" />
          Logística
        </TabsTrigger>
      </TabsList>

      <TabsContent value="general" className="space-y-4 pt-4">
        <WeddingOverview
          wedding={wedding}
          overview={overview}
          onNavigateToPlanning={() => {
            setSearchParams((prev) => {
              prev.set("tab", "planning");
              prev.set("subtab", "checklist");
              return prev;
            }, { replace: true });
          }}
          onNavigateToFinances={() => {
            setSearchParams((prev) => {
              prev.set("tab", "finances");
              return prev;
            }, { replace: true });
          }}
        />
      </TabsContent>

      <TabsContent value="finances" className="space-y-4 pt-4">
        <Suspense fallback={null}>
          <WeddingFinancesView weddingUuid={wedding.uuid} />
        </Suspense>
      </TabsContent>

      <TabsContent value="logistics" className="space-y-4 pt-4">
        <Suspense fallback={null}>
          <WeddingVendorsItemsTab weddingUuid={wedding.uuid} />
        </Suspense>
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
            <Suspense fallback={null}>
              <WeddingTimelineTab weddingUuid={wedding.uuid} />
            </Suspense>
          </TabsContent>
          <TabsContent value="checklist">
            <Suspense fallback={null}>
              <WeddingChecklistTab weddingUuid={wedding.uuid} />
            </Suspense>
          </TabsContent>
        </Tabs>
      </TabsContent>
    </Tabs>
  );
}
