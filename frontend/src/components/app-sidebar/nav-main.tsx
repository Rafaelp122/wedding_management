import { Link, useLocation } from "react-router-dom";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface NavItem {
  title: string;
  path: string;
  icon: LucideIcon;
}

export function NavMain({ items }: { items: NavItem[] }) {
  const location = useLocation();

  return (
    <SidebarMenu className="p-2 gap-1">
      {items.map((item) => {
        const isActive = location.pathname.startsWith(item.path);
        return (
          <SidebarMenuItem key={item.path}>
            <SidebarMenuButton
              asChild
              tooltip={item.title}
              isActive={isActive}
              className={cn(
                "relative px-3 py-2.5 h-10 transition-all duration-150 rounded-lg",
                "[&>svg]:!size-5",
                "group-data-[collapsible=icon]:!size-10",
                isActive
                  ? "bg-secondary text-primary font-medium before:absolute before:left-0 before:top-2 before:bottom-2 before:w-1 before:bg-primary before:rounded-r-full"
                  : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/50 dark:hover:text-zinc-100 font-medium",
              )}
            >
              <Link to={item.path} className="flex items-center w-full">
                <item.icon
                  className={cn(
                    "size-5 shrink-0",
                    isActive
                      ? "text-primary"
                      : "text-zinc-400 dark:text-zinc-500",
                  )}
                />
                <span className="truncate">{item.title}</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        );
      })}
    </SidebarMenu>
  );
}
