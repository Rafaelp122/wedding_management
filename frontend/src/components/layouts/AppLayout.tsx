import { Outlet } from "react-router-dom";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";

import { useAuthStore } from "@/stores/authStore";
import { User as UserIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AppSidebar } from "../app-sidebar";

export const AppLayout = () => {
  const user = useAuthStore((state) => state.user);

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <AppSidebar />

        <main className="flex-1 flex flex-col overflow-hidden bg-muted/5">
          {/* Header Minimalista */}
          <header className="flex h-16 shrink-0 items-center justify-between border-b px-6 bg-background transition-[width,height] ease-linear">
            <div className="flex items-center gap-4">
              <SidebarTrigger />
              <Separator orientation="vertical" className="h-6" />
              <h1 className="font-semibold text-lg">Painel de Controle</h1>
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
          <div className="flex-1 overflow-y-auto p-6 md:p-8">
            <Outlet />
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
};
