import { Link, useLocation } from "react-router-dom";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import type { LucideIcon } from "lucide-react";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";

interface NavItem {
  title: string;
  path: string;
  icon: LucideIcon;
}

export function NavMain({ items }: { items: NavItem[] }) {
  const location = useLocation();
  const { data: weddingsRes } = useWeddingsList();
  const weddingsCount = weddingsRes?.data?.count ?? weddingsRes?.data?.items?.length ?? 0;

  return (
    <SidebarMenu className="p-2 gap-1">
      {items.map((item) => {
        const isActive = location.pathname.startsWith(item.path);
        const isWeddings = item.path === "/weddings";
        return (
          <SidebarMenuItem key={item.path}>
            <SidebarMenuButton
              asChild
              tooltip={item.title}
              isActive={isActive}
              className={`relative px-3 py-2.5 h-10 transition-all duration-150 rounded-lg ${
                isActive
                  ? "bg-secondary text-primary font-medium before:absolute before:left-0 before:top-2 before:bottom-2 before:w-1 before:bg-primary before:rounded-r-full"
                  : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/50 dark:hover:text-zinc-100 font-medium"
              }`}
            >
              <Link to={item.path} className="flex items-center w-full">
                <item.icon className={`w-5 h-5 shrink-0 ${isActive ? "text-primary" : "text-zinc-400 dark:text-zinc-500"}`} />
                <span className="truncate">{item.title}</span>
                {isWeddings && (
                  <span className="ml-auto bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 py-0.5 px-2 rounded-full text-xs font-mono group-data-[collapsible=icon]:hidden">
                    {weddingsCount}
                  </span>
                )}
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        );
      })}
    </SidebarMenu>
  );
}
