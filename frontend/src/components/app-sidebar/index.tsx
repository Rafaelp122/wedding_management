import {
  LayoutDashboard,
  Heart,
  Calendar,
  Handshake,
  Settings,
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
  { title: "Fornecedores", path: "/suppliers", icon: Handshake },
  { title: "Cronograma Geral", path: "/scheduler", icon: Calendar },
  { title: "Configurações", path: "/settings", icon: Settings },
];

export function AppSidebar() {
  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="h-16 flex items-center justify-center">
        <span className="font-bold text-xl text-primary group-data-[collapsible=icon]:hidden">
          Wedding Admin
        </span>
        <Heart className="h-6 w-6 text-primary hidden group-data-[collapsible=icon]:block" />
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
