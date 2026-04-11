import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Outlet, useLocation } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/authStore";
import { User as UserIcon } from "lucide-react";
import { AppSidebar } from "../app-sidebar";

const PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/weddings": "Casamentos",
  "/agenda": "Agenda",
  "/suppliers": "Fornecedores",
  "/settings": "Configurações",
};

export const AppLayout = () => {
  const user = useAuthStore((state) => state.user);
  const { pathname } = useLocation();
  const pageTitle = pathname.startsWith("/weddings/")
    ? "Detalhes do Casamento"
    : PAGE_TITLES[pathname] ?? "Painel de Controle";

  return (
    <SidebarProvider>
      <AppSidebar />

      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center justify-between border-b px-6 bg-background transition-[width,height] ease-linear">
          <div className="flex items-center gap-4">
            <SidebarTrigger />
            <Separator orientation="vertical" className="h-6" />
            <h1 className="font-semibold text-lg">{pageTitle}</h1>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-sm font-medium hidden md:inline-block">
              Olá, {user?.first_name}
            </span>
            <Button variant="outline" size="icon" className="rounded-full">
              <UserIcon className="h-4 w-4" />
            </Button>
          </div>
        </header>

        {/* Conteúdo com Scroll Independente */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-muted/5">
          <Outlet />
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
};
