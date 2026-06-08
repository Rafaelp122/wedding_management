import { useState } from "react";
import {
  LayoutDashboard,
  Heart,
  Calendar,
  Handshake,
  Settings,
  PanelLeft,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  useSidebar,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { NavMain } from "./nav-main";
import { NavUser } from "./nav-user";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";

const menuItems = [
  { title: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { title: "Casamentos", path: "/weddings", icon: Heart },
  { title: "Fornecedores", path: "/suppliers", icon: Handshake },
  { title: "Cronograma Geral", path: "/scheduler", icon: Calendar },
  { title: "Configurações", path: "/settings", icon: Settings },
];

const RingsIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="9" cy="13" r="5.5" />
    <circle cx="15" cy="11" r="5.5" />
  </svg>
);

export function AppSidebar() {
  const { state, toggleSidebar } = useSidebar();
  const [isLogoHovered, setIsLogoHovered] = useState(false);

  const handleLogoClick = () => {
    setIsLogoHovered(false);
    toggleSidebar();
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="h-16 flex flex-row items-center justify-between p-2 transition-all duration-200 overflow-visible">
        {state === "collapsed" ? (
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={handleLogoClick}
                onMouseEnter={() => setIsLogoHovered(true)}
                onMouseLeave={() => setIsLogoHovered(false)}
                className="size-8 rounded-lg bg-primary flex items-center justify-center shadow-[0_0_15px_rgba(124,58,237,0.3)] shrink-0 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring cursor-pointer mx-auto"
                aria-label="Abrir barra lateral"
              >
                {isLogoHovered ? (
                  <PanelLeft className="size-[18px] text-primary-foreground" />
                ) : (
                  <RingsIcon className="size-[18px] text-primary-foreground" />
                )}
              </button>
            </TooltipTrigger>
            <TooltipContent side="right" align="center">
              Abrir barra lateral
            </TooltipContent>
          </Tooltip>
        ) : (
          <div className="flex items-center justify-between w-full px-3 h-10 animate-in fade-in duration-200">
            <div className="flex items-center">
              <div className="size-8 rounded-lg bg-primary flex items-center justify-center shadow-[0_0_15px_rgba(124,58,237,0.3)] shrink-0">
                <RingsIcon className="size-[18px] text-primary-foreground" />
              </div>
              <span className="font-bold text-xl tracking-tight text-zinc-900 dark:text-white ml-3 truncate font-display">
                Sim, Aceito!
              </span>
            </div>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-8 text-zinc-500 hover:text-zinc-950 dark:text-zinc-400 dark:hover:text-zinc-50 rounded-lg ml-auto focus-visible:ring-2 focus-visible:ring-ring"
                  onClick={toggleSidebar}
                  aria-label="Fechar barra lateral"
                >
                  <PanelLeft className="size-[18px]" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right" align="center">
                Fechar barra lateral
              </TooltipContent>
            </Tooltip>
          </div>
        )}
      </SidebarHeader>
      <Separator className="bg-zinc-100 dark:bg-zinc-800/50" />
      <SidebarContent>
        <NavMain items={menuItems} />
      </SidebarContent>
      <SidebarFooter className="p-4 group-data-[collapsible=icon]:p-2 bg-zinc-50/50 dark:bg-zinc-900/50 border-t border-zinc-200 dark:border-zinc-800">
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  );
}
