import { Outlet, Link } from "react-router-dom";
import { Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export const PublicLayout = () => {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* HEADER / NAVBAR */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
        <div className="container flex h-16 items-center justify-between mx-auto px-4 md:px-8">
          {/* LOGO */}
          <Link
            to="/"
            className="flex items-center gap-2 transition-opacity hover:opacity-80"
          >
            <Heart className="h-6 w-6 text-pink-500 fill-pink-500" />
            <span className="text-xl font-bold tracking-tight">
              WeddingSystem
            </span>
          </Link>

          {/* NAVEGAÇÃO / AÇÕES */}
          <nav className="flex items-center gap-4">
            <Button variant="ghost" asChild>
              <Link to="/login">Entrar</Link>
            </Button>
            <Button asChild>
              <Link to="/login">Começar Agora</Link>
            </Button>
          </nav>
        </div>
      </header>

      {/* CONTEÚDO PRINCIPAL */}
      <main className="flex-1">
        {/* O Outlet aqui renderiza a Home ou a tela de Login/Registro.
            Sem o Outlet, suas rotas filhas são invisíveis.
        */}
        <Outlet />
      </main>

      <Separator />

      {/* FOOTER */}
      <footer className="w-full border-t bg-muted/40 py-8">
        <div className="container mx-auto px-4 md:px-8">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="flex items-center gap-2">
              <Heart className="h-4 w-4 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                © 2026 WeddingSystem. Gerenciando sonhos com lógica fria.
              </p>
            </div>
            <div className="flex gap-6 text-sm font-medium text-muted-foreground">
              <span className="cursor-default">Privacidade</span>
              <span className="cursor-default">Termos de Uso</span>
              <span className="cursor-default">Contato</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
