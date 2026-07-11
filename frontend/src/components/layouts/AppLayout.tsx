import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Outlet, useLocation, Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Bell, ChevronRight, ChevronDown, Check } from "lucide-react";
import { AppSidebar } from "../app-sidebar";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuTrigger,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { useWeddingsRead, useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

const PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Dashboard Geral",
  "/weddings": "Casamentos",
  "/scheduler": "Scheduler",
  "/suppliers": "Fornecedores",
  "/settings": "Configurações",
};

export const AppLayout = () => {
  const { pathname } = useLocation();

  // Match /weddings/:uuid (ignoring trailing slash or query params)
  const match = pathname.match(/^\/weddings\/([^/]+)$/);
  const weddingUuid = match ? match[1] : null;

  const { data: weddingResponse, isLoading: isLoadingWedding } = useWeddingsRead(
    weddingUuid ?? "",
    { query: { enabled: !!weddingUuid } }
  );
  const wedding = weddingResponse?.data;

  const { data: weddingsListResponse } = useWeddingsList(
    undefined,
    { query: { enabled: !!weddingUuid } }
  );
  const weddingsList = weddingsListResponse?.data?.items ?? [];

  const pageTitle = pathname.startsWith("/weddings/")
    ? "Detalhes do Casamento"
    : pathname.startsWith("/suppliers/")
      ? "Detalhes do Fornecedor"
      : (PAGE_TITLES[pathname] ?? "Painel de Controle");

  useDocumentTitle(
    pathname.startsWith("/weddings/") && wedding
      ? `Casamento: ${wedding.groom_name} & ${wedding.bride_name}`
      : pageTitle
  );

  return (
    <SidebarProvider>
      <AppSidebar />

      <SidebarInset className="flex flex-col h-svh overflow-hidden">
        <header className="shrink-0 flex h-16 items-center justify-between border-b px-6 bg-white/80 dark:bg-[#18181B]/80 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <SidebarTrigger className="md:hidden" />
            <Separator orientation="vertical" className="h-6 md:hidden" />

            {weddingUuid ? (
              isLoadingWedding ? (
                <>
                  <Skeleton className="h-6 w-48 hidden sm:block" />
                  <Skeleton className="h-6 w-24 sm:hidden" />
                </>
              ) : wedding ? (
                <>
                  <div className="hidden sm:flex items-center text-sm text-zinc-500 dark:text-zinc-400 font-medium">
                    <Link
                      to="/weddings"
                      className="hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors cursor-pointer"
                    >
                      Casamentos
                    </Link>
                    <ChevronRight className="w-4 h-4 mx-2 text-zinc-300 dark:text-zinc-600" />
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <button className="flex items-center gap-1 hover:text-zinc-900 dark:hover:text-zinc-100 font-semibold text-primary cursor-pointer select-none transition-colors focus:outline-none">
                          {wedding.groom_name} & {wedding.bride_name}
                          <ChevronDown className="w-4 h-4 opacity-75" />
                        </button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="start" className="w-56">
                        {weddingsList.map((w) => (
                          <DropdownMenuItem
                            key={w.uuid}
                            asChild
                            className={cn(
                              "cursor-pointer",
                              w.uuid === wedding.uuid && "bg-accent/50 text-accent-foreground font-semibold"
                            )}
                          >
                            <Link
                              to={`/weddings/${w.uuid}`}
                              className="w-full flex justify-between items-center"
                            >
                              <span>
                                {w.groom_name} & {w.bride_name}
                              </span>
                              {w.uuid === wedding.uuid && (
                                <Check className="w-4 h-4 text-primary ml-2 shrink-0" />
                              )}
                            </Link>
                          </DropdownMenuItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                  {/* Mobile-only switcher/title */}
                  <div className="sm:hidden">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <button className="flex items-center gap-1 font-semibold text-primary text-base cursor-pointer select-none transition-colors focus:outline-none">
                          {wedding.groom_name} & {wedding.bride_name}
                          <ChevronDown className="w-4 h-4 opacity-75" />
                        </button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="start" className="w-56">
                        {weddingsList.map((w) => (
                          <DropdownMenuItem
                            key={w.uuid}
                            asChild
                            className={cn(
                              "cursor-pointer",
                              w.uuid === wedding.uuid && "bg-accent/50 text-accent-foreground font-semibold"
                            )}
                          >
                            <Link
                              to={`/weddings/${w.uuid}`}
                              className="w-full flex justify-between items-center"
                            >
                              <span>
                                {w.groom_name} & {w.bride_name}
                              </span>
                              {w.uuid === wedding.uuid && (
                                <Check className="w-4 h-4 text-primary ml-2 shrink-0" />
                              )}
                            </Link>
                          </DropdownMenuItem>
                        ))}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </>
              ) : (
                <h1 className="font-semibold text-lg text-primary">{pageTitle}</h1>
              )
            ) : (
              <h1 className="font-semibold text-lg text-primary">{pageTitle}</h1>
            )}
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
                  <Bell aria-hidden="true" className="w-5 h-5" />
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
