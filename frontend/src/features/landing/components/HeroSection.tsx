import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export function HeroSection() {
  return (
    <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-linear-to-b from-white to-primary/5 dark:from-background dark:to-muted/20">
      <div className="container px-4 md:px-6 mx-auto text-center flex flex-col gap-4">
        <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl">
          Gerencie Casamentos com{" "}
          <span className="text-primary">Precisão</span>
        </h1>
        <p className="mx-auto max-w-175 text-muted-foreground md:text-xl">
          De orçamentos a cronogramas. A ferramenta definitiva para assessores.
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild size="lg">
            <Link to="/register">Começar agora</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link to="/login">Acessar painel</Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
