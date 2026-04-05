import {
  LayoutDashboard,
  Heart,
  Calendar,
  FileText,
  DollarSign,
  Package,
  Receipt,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { NavMain } from "./nav-main";
import { NavUser } from "./nav-user";

const menuItems = [
  { title: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { title: "Casamentos", path: "/weddings", icon: Heart },
  { title: "Agenda", path: "/scheduler", icon: Calendar },
  { title: "Contratos", path: "/logistics/contracts", icon: FileText },
  { title: "Itens", path: "/logistics/items", icon: Package },
  { title: "Orçamentos", path: "/finances/budgets", icon: DollarSign },
  { title: "Despesas", path: "/finances/expenses", icon: Receipt },
];

export function AppSidebar() {
  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="h-16 flex items-center justify-center">
        <span className="font-bold text-xl text-pink-600 group-data-[collapsible=icon]:hidden">
          Wedding Admin
        </span>
        <Heart className="h-6 w-6 text-pink-600 hidden group-data-[collapsible=icon]:block" />
      </SidebarHeader>
      <Separator />
      <SidebarContent>
        <NavMain items={menuItems} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  );
}
