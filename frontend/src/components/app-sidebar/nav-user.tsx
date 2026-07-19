import { useAuthStore } from "@/stores/authStore";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useTheme } from "next-themes";
import { useSidebar } from "@/components/ui/sidebar";
import { NavUserView } from "./NavUserView";

export function NavUser() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { theme, setTheme } = useTheme();
  const { state } = useSidebar();
  const queryClient = useQueryClient();

  const handleLogout = () => {
    queryClient.clear();
    logout();
    navigate("/login");
  };

  const handleToggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  if (!user) return null;

  return (
    <NavUserView
      user={user}
      theme={theme}
      onToggleTheme={handleToggleTheme}
      isCollapsed={state === "collapsed"}
      onNavigate={navigate}
      onLogout={handleLogout}
    />
  );
}
