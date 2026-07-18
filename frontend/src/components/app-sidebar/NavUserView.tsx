import { LogOut, User as UserIcon, Moon, Sun, MoreVertical, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import type { UserDataOut } from "@/api/generated/v1/models/userDataOut";

export interface NavUserViewProps {
  user: UserDataOut;
  theme?: string;
  onToggleTheme: () => void;
  isCollapsed: boolean;
  onNavigate: (path: string) => void;
  onLogout: () => void;
}

export function NavUserView({
  user,
  theme,
  onToggleTheme,
  isCollapsed,
  onNavigate,
  onLogout,
}: NavUserViewProps) {
  const userInitials = user.first_name?.[0]?.toUpperCase() || "";

  return (
    <div className="flex flex-col w-full">
      {!isCollapsed ? (
        <div className="flex flex-col animate-in fade-in duration-200">
          {/* Row 1: Tema */}
          <div className="flex items-center justify-between mb-4 px-2 text-xs font-medium text-zinc-500 dark:text-zinc-400">
            <span>Tema</span>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100 rounded-lg cursor-pointer transition-colors"
              onClick={onToggleTheme}
              aria-label="Alternar tema"
            >
              <Sun aria-hidden="true" className="h-[18px] w-[18px] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon aria-hidden="true" className="absolute h-[18px] w-[18px] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            </Button>
          </div>

          {/* Row 2: User profile info */}
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="h-10 w-10 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center text-primary font-bold shrink-0 border-2 border-white dark:border-zinc-800 shadow-sm">
                {userInitials || <UserIcon aria-hidden="true" className="h-4.5 w-4.5" />}
              </div>
              <div className="flex flex-col overflow-hidden text-left">
                <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 truncate leading-none font-display">
                  {user.first_name} {user.last_name}
                </span>
                <span className="text-xs text-zinc-500 dark:text-zinc-400 truncate mt-1.5 leading-none">
                  {user.email}
                </span>
              </div>
            </div>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 text-zinc-400 hover:text-zinc-950 dark:hover:text-zinc-50 rounded-lg cursor-pointer ml-auto focus-visible:ring-2 focus-visible:ring-ring"
                  aria-label="Menu do usuário"
                >
                  <MoreVertical aria-hidden="true" className="h-[18px] w-[18px]" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" side="top" className="w-48">
                <DropdownMenuItem className="cursor-pointer gap-2" onClick={() => onNavigate("/settings")}>
                  <UserIcon aria-hidden="true" className="h-4 w-4" />
                  Minha Conta
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer gap-2" onClick={() => onNavigate("/settings")}>
                  <Settings aria-hidden="true" className="h-4 w-4" />
                  Configurações
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="text-destructive focus:bg-destructive/10 focus:text-destructive cursor-pointer gap-2"
                  onClick={onLogout}
                >
                  <LogOut aria-hidden="true" className="h-4 w-4" />
                  Sair
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      ) : (
        /* Collapsed State */
        <div className="flex flex-col items-center justify-center animate-in fade-in duration-200">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="h-10 w-10 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center text-primary font-bold shrink-0 border-2 border-white dark:border-zinc-800 shadow-sm cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-label="Menu do usuário"
              >
                {userInitials || <UserIcon aria-hidden="true" className="h-4.5 w-4.5" />}
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" side="right" className="w-56">
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{user.first_name} {user.last_name}</p>
                  <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer gap-2" onClick={() => onNavigate("/settings")}>
                <UserIcon aria-hidden="true" className="h-4 w-4" />
                Minha Conta
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer gap-2" onClick={() => onNavigate("/settings")}>
                <Settings aria-hidden="true" className="h-4 w-4" />
                Configurações
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="cursor-pointer gap-2"
                onClick={onToggleTheme}
              >
                {theme === "dark" ? (
                  <>
                    <Sun aria-hidden="true" className="h-4 w-4" />
                    Modo Claro
                  </>
                ) : (
                  <>
                    <Moon aria-hidden="true" className="h-4 w-4" />
                    Modo Escuro
                  </>
                )}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-destructive focus:bg-destructive/10 focus:text-destructive cursor-pointer gap-2"
                onClick={onLogout}
              >
                <LogOut aria-hidden="true" className="h-4 w-4" />
                Sair
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}
    </div>
  );
}
