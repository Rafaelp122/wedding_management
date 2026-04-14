import { LogOut, User as UserIcon } from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/themeToggle";

export function NavUser() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!user) return null;

  return (
    <div className="flex flex-col gap-2 p-2 group-data-[collapsible=icon]:p-0">
      {/* Expanded view */}
      <div className="flex flex-col gap-2 group-data-[collapsible=icon]:hidden">
        <div className="flex items-center justify-between gap-3 px-2 py-1.5">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="h-8 w-8 rounded-full bg-primary-foreground flex items-center justify-center text-primary font-bold shrink-0">
              {user.first_name?.[0] || <UserIcon className="h-4 w-4" />}
            </div>
            <div className="flex flex-col overflow-hidden text-left">
              <span className="text-sm font-medium truncate">
                {user.first_name} {user.last_name}
              </span>
              <span className="text-xs text-muted-foreground truncate">
                {user.email}
              </span>
            </div>
          </div>
          <ThemeToggle />
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start gap-2 text-destructive hover:bg-destructive/10 hover:text-destructive"
          onClick={handleLogout}
        >
          <LogOut className="h-4 w-4" />
          Sair
        </Button>
      </div>

      {/* Collapsed view */}
      <div className="hidden flex-col items-center gap-2 group-data-[collapsible=icon]:flex pb-2">
        <div className="h-8 w-8 rounded-full bg-primary-foreground flex items-center justify-center text-primary font-bold shrink-0 mb-1">
          {user.first_name?.[0] || <UserIcon className="h-4 w-4" />}
        </div>
        <ThemeToggle />
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 text-destructive hover:bg-destructive/10 hover:text-destructive"
          onClick={handleLogout}
        >
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
