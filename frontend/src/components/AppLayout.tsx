import { Outlet, Link } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { Button } from "@/components/button";
import { LogOut, Calendar, FileText, Package, Heart } from "lucide-react";

export function AppLayout() {
  const { user, logout } = useAuthStore();

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-8">
              <Link to="/dashboard" className="flex items-center gap-2">
                <Heart className="h-6 w-6 text-primary" />
                <span className="text-xl font-bold">Wedding Management</span>
              </Link>
              <div className="hidden md:flex items-center gap-4">
                <Link
                  to="/dashboard"
                  className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  to="/weddings"
                  className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                >
                  <Heart className="h-4 w-4" />
                  Weddings
                </Link>
                <Link
                  to="/scheduler"
                  className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                >
                  <Calendar className="h-4 w-4" />
                  Scheduler
                </Link>
                <Link
                  to="/contracts"
                  className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                >
                  <FileText className="h-4 w-4" />
                  Contracts
                </Link>
                <Link
                  to="/items"
                  className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                >
                  <Package className="h-4 w-4" />
                  Items
                </Link>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">
                {user?.first_name} {user?.last_name}
              </span>
              <Button onClick={logout} variant="outline" size="sm">
                <LogOut className="h-4 w-4 mr-2" />
                Sair
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto py-6 px-4">
        <Outlet />
      </main>
    </div>
  );
}
