import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Outlet, useLocation } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Search, Bell } from "lucide-react";
import { AppSidebar } from "../app-sidebar";

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
      : PAGE_TITLES[pathname] ?? "Painel de Controle";

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
            {/* Search */}
            <div className="relative hidden md:block">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="w-4 h-4 text-zinc-400" />
              </div>
              <input
                type="text"
                aria-label="Buscar fornecedor, evento"
                className="block w-64 pl-10 pr-12 py-2 border border-zinc-200 dark:border-zinc-700 rounded-lg bg-zinc-50 dark:bg-zinc-900/50 text-sm placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all text-zinc-900 dark:text-zinc-100"
                placeholder="Buscar fornecedor, evento..."
              />
              <div className="absolute inset-y-0 right-0 pr-2 flex items-center pointer-events-none">
                <span className="text-xs text-zinc-400 font-mono bg-white dark:bg-zinc-800 px-1.5 py-0.5 rounded border border-zinc-200 dark:border-zinc-700">
                  ⌘&nbsp;K
                </span>
              </div>
            </div>

            {/* Notifications */}
            <Button
              variant="ghost"
              size="icon"
              className="relative text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 focus-visible:ring-primary/50"
              aria-label="Notificações"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-destructive rounded-full ring-2 ring-white dark:ring-[#18181B]" />
            </Button>
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
