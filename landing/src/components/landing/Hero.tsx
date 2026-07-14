import { useState } from "react";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";

interface HeroProps {
  onOpenLead: (email?: string) => void;
}

export function Hero({ onOpenLead }: HeroProps) {
  const [leadEmail, setLeadEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onOpenLead(leadEmail);
  };

  return (
    <section
      id="overview"
      className="pt-32 pb-20 md:pt-40 md:pb-32 px-6 md:px-12 max-w-7xl mx-auto relative z-10"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-6 space-y-6 md:space-y-8 flex flex-col items-start">
          <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/20 text-primary px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider animate-soft-pulse">
            <Sparkles className="w-3.5 h-3.5 fill-primary" />
            <span>Lançamento Premium 2026</span>
          </div>

          <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-foreground tracking-tight leading-[1.05] text-left">
            Gestão impecável para assessorar{" "}
            <span className="text-primary bg-gradient-to-r from-primary to-primary/80 bg-clip-text text-transparent">
              sem estresse.
            </span>
          </h1>

          <p className="text-base md:text-lg text-muted-foreground font-medium max-w-xl text-left leading-relaxed">
            A solução completa e inteligente para organizar casamentos, gerenciar finanças e encantar noivos em uma única plataforma integrada.
          </p>

          <form onSubmit={handleSubmit} className="w-full max-w-md">
            <div className="relative flex items-center bg-card rounded-full p-1.5 border border-border shadow-lg hover:border-primary/50 focus-within:border-primary focus-within:ring-4 focus-within:ring-primary/10 transition-all duration-300">
              <Input
                type="email"
                placeholder="Seu e-mail profissional"
                value={leadEmail}
                onChange={(e) => setLeadEmail(e.target.value)}
                required
                className="flex-grow bg-transparent border-none focus:ring-0 text-sm md:text-base px-5 py-3 text-foreground placeholder:text-muted-foreground/50 focus:outline-none"
              />
              <Button
                type="submit"
                className="bg-primary hover:bg-primary-hover text-white text-xs md:text-sm font-bold py-3.5 px-6 rounded-full hover:shadow-lg hover:shadow-primary/20 transition-all duration-150 flex items-center whitespace-nowrap gap-2 shrink-0 cursor-pointer"
              >
                <span>Começar Grátis</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </form>
        </div>

        <div className="lg:col-span-6 relative h-[500px] lg:h-[600px] flex items-center justify-center">
          <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 to-primary/10 rounded-[3rem] rotate-3 transform-gpu z-0"></div>

          <div className="absolute top-6 left-6 md:left-12 bg-card rounded-2xl shadow-xl border border-border/20 p-3.5 flex items-center gap-3.5 z-30 animate-[bounce_6s_infinite] max-w-[280px]">
            <img
              src="https://i.pravatar.cc/150?img=47"
              alt="Noivos"
              referrerPolicy="no-referrer"
              loading="lazy"
              onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
              className="w-12 h-12 rounded-full object-cover shadow-sm ring-2 ring-primary/20"
            />
            <div>
              <p className="text-xs font-black text-foreground leading-tight">Próximo Casamento</p>
              <p className="text-[10px] text-muted-foreground font-semibold mt-0.5">Maria & João - 28 de Outubro</p>
            </div>
          </div>

          <div className="absolute bottom-10 left-[-10px] md:left-[-30px] bg-card rounded-2xl shadow-xl border border-border/20 p-3.5 flex items-center gap-3.5 z-30 animate-[bounce_7s_infinite_1s] max-w-[280px]">
            <img
              src="https://i.pravatar.cc/150?img=32"
              alt="Casal 2"
              referrerPolicy="no-referrer"
              loading="lazy"
              onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
              className="w-10 h-10 rounded-full object-cover shadow-sm ring-2 ring-primary/20"
            />
            <div>
              <p className="text-xs font-black text-foreground leading-tight">Cronograma Enviado</p>
              <p className="text-[10px] text-muted-foreground font-semibold mt-0.5">Beatriz & Rafael - Pendente RSVP</p>
            </div>
          </div>

          <div className="w-[85%] md:w-[90%] bg-card rounded-3xl p-6 shadow-2xl border border-border/30 z-10 transform translate-y-2 hover:scale-[1.02] transition-transform duration-500">
            <div className="flex justify-between items-center mb-5">
              <h3 className="font-extrabold text-base md:text-lg text-foreground">Dashboard Financeiro</h3>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full uppercase">
                Ativo
              </span>
            </div>

            <div className="h-24 mb-6 relative overflow-hidden rounded-xl bg-muted border border-border/20 flex items-end">
              <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 400 100">
                <path
                  d="M0,80 C50,80 100,40 150,60 C200,80 250,20 300,40 C350,60 400,10 400,10 L400,100 L0,100 Z"
                  fill="var(--primary)"
                  fillOpacity="0.08"
                ></path>
                <path
                  d="M0,80 C50,80 100,40 150,60 C200,80 250,20 300,40 C350,60 400,10 400,10"
                  fill="none"
                  style={{ stroke: "var(--primary)" }}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                ></path>
              </svg>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 border-t border-border/20 pt-4">
              <div>
                <p className="text-[10px] uppercase text-muted-foreground font-semibold tracking-wider mb-0.5">
                  Recebido
                </p>
                <p className="text-sm md:text-base font-extrabold text-foreground">R$ 24.500,00</p>
              </div>
              <div>
                <p className="text-[10px] uppercase text-muted-foreground font-semibold tracking-wider mb-0.5">
                  Pendentes
                </p>
                <p className="text-sm md:text-base font-extrabold text-red-600">R$ 3.200,00</p>
              </div>
              <div className="hidden md:block">
                <p className="text-[10px] uppercase text-muted-foreground font-semibold tracking-wider mb-0.5">
                  Previsão
                </p>
                <p className="text-sm md:text-base font-extrabold text-emerald-600">R$ 27.700,00</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
