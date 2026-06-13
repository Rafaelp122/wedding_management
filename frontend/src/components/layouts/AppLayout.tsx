import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Outlet, useLocation } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Bell } from "lucide-react";
import { AppSidebar } from "../app-sidebar";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Dashboard Geral",
  "/weddings": "Casamentos",
  "/scheduler": "Scheduler",
  "/suppliers": "Fornecedores",
  "/settings": "Configurações",
};

export const AppLayout = () => {
  const { pathname } = useLocation();
  const pageTitle = pathname.startsWith("/weddings/")
    ? "Detalhes do Casamento"
    : pathname.startsWith("/suppliers/")
      ? "Detalhes do Fornecedor"
      : (PAGE_TITLES[pathname] ?? "Painel de Controle");

  useDocumentTitle(pageTitle);

  return (
    <SidebarProvider>
      <AppSidebar />

      <SidebarInset className="flex flex-col h-svh overflow-hidden">
        <header className="shrink-0 flex h-16 items-center justify-between border-b px-6 bg-white/80 dark:bg-[#18181B]/80 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <SidebarTrigger className="md:hidden" />
            <Separator orientation="vertical" className="h-6 md:hidden" />
            <h1 className="font-semibold text-lg text-primary">{pageTitle}</h1>
          </div>

          <div className="flex items-center gap-4">
            {/* Notifications */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="relative text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 focus-visible:ring-primary/50 cursor-pointer"
                  aria-label="Notificações"
                >
                  <Bell className="w-5 h-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80">
                <DropdownMenuLabel>Notificações</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <div className="p-4 text-center text-xs text-zinc-500 dark:text-zinc-400">
                  Você não tem novas notificações no momento.
                </div>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Conteúdo com Scroll Independente */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-background min-h-0">
          <Outlet />
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
};
