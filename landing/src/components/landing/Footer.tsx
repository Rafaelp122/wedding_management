import { useState } from "react";
import { Send, CheckCircle2 } from "lucide-react";
import { Input } from "../ui/input";
import { Button } from "../ui/button";

export function Footer() {
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);
  const [error, setError] = useState("");

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setError("Por favor, insira um e-mail.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)) {
      setError("Por favor, insira um e-mail válido.");
      return;
    }
    setError("");
    setSubscribed(true);
    setEmail("");
    setTimeout(() => setSubscribed(false), 5000);
  };

  return (
    <footer className="bg-card border-t border-border pt-16 pb-8 text-foreground">
      <div className="max-w-7xl mx-auto px-6 md:px-12 grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
        <div className="md:col-span-1 flex flex-col gap-4">
          <a href="#" className="flex items-center gap-3 text-xl font-bold tracking-tight text-foreground">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="9" cy="13" r="5.5" />
                <circle cx="15" cy="11" r="5.5" />
              </svg>
            </div>
            <span>Sim, Aceito!</span>
          </a>
          <p className="text-muted-foreground text-sm leading-relaxed max-w-sm">
            O primeiro e único ERP de gestão completa projetado exclusivamente para assessores de casamentos de alta performance. Organização sem estresse.
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <h4 className="font-bold text-base text-foreground tracking-wide uppercase text-xs opacity-60 mb-2">Recursos</h4>
          <a href="#features" className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium">Dashboard Financeiro</a>
          <a href="#features" className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium">Checklists Inteligentes</a>
          <a href="#features" className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium">Diretório de Fornecedores</a>
          <a href="#process" className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium">Metodologia Operacional</a>
        </div>

        <div className="flex flex-col gap-3">
          <h4 className="font-bold text-base text-foreground tracking-wide uppercase text-xs opacity-60 mb-2">Institucional</h4>
          <a href="#" className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium">Termos de Uso</a>
          <a href="#" className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium">Políticas de Privacidade</a>
          <a href="#" className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium">Fale Conosco</a>
          <a href="#" className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium">Trabalhe Conosco</a>
        </div>

        <div className="flex flex-col gap-3">
          <h4 className="font-bold text-base text-foreground tracking-wide uppercase text-xs opacity-60 mb-2">Fique Atualizado</h4>
          <p className="text-muted-foreground text-sm">
            Inscreva-se na nossa newsletter para receber artigos exclusivos sobre tendências do mercado de casamentos.
          </p>

          {subscribed ? (
            <div className="bg-emerald-50 text-emerald-800 p-3.5 rounded-xl border border-emerald-200 flex items-center gap-2 text-xs font-semibold">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>Inscrição realizada com sucesso!</span>
            </div>
          ) : (
            <div>
              <form onSubmit={handleSubscribe} className="relative flex items-center mt-2">
              <Input
                type="email"
                placeholder="Seu e-mail"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full pl-4 pr-12 py-2.5 rounded-xl border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary bg-muted"
              />
              <Button
                type="submit"
                className="absolute right-1.5 p-1.5 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors"
                aria-label="Inscrever-se"
              >
                <Send className="w-4 h-4" />
              </Button>
            </form>
              {error && (
                <p className="text-red-500 text-xs font-medium mt-1.5">{error}</p>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 md:px-12 border-t border-border pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-center">
        <p className="text-muted-foreground text-sm">
          © 2026 Sim, Aceito! ERP para Assessoria de Eventos. Todos os direitos reservados.
        </p>
        <p className="text-xs text-muted-foreground/60 flex items-center gap-1.5 justify-center">
          <span>Feito com</span>
          <span className="text-primary">♥</span>
          <span>para os melhores assessores do Brasil</span>
        </p>
      </div>
    </footer>
  );
}
