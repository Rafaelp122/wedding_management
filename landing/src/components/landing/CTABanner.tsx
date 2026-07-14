import { Heart, ArrowRight, ChevronRight, ShieldCheck } from "lucide-react";
import { Button } from "../ui/button";

interface CTABannerProps {
  onOpenLead: () => void;
}

export function CTABanner({ onOpenLead }: CTABannerProps) {
  return (
    <section className="py-16 md:py-20 bg-primary relative z-10 overflow-hidden text-white">
      <div className="absolute top-[-100px] left-[-100px] w-[300px] h-[300px] bg-white/5 rounded-full blur-2xl"></div>
      <div className="absolute bottom-[-100px] right-[-100px] w-[300px] h-[300px] bg-white/5 rounded-full blur-2xl"></div>

      <div className="max-w-4xl mx-auto px-6 md:px-12 text-center space-y-6 md:space-y-8 relative z-10">
        <Heart className="w-12 h-12 text-white fill-white mx-auto animate-pulse" />
        <h2 className="text-3xl md:text-4xl font-black tracking-tight leading-tight">
          Pronta para elevar o padrão da sua assessoria?
        </h2>
        <p className="text-base md:text-lg text-white/85 max-w-2xl mx-auto font-medium leading-relaxed">
          Junte-se a centenas de profissionais sênior que já automatizaram suas finanças, checklists e atendimento com o Sim, Aceito!. Comece seu teste gratuito de 14 dias em menos de 1 minuto.
        </p>
        <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
          <Button
            onClick={onOpenLead}
            className="w-full sm:w-auto bg-white hover:bg-muted text-primary font-black text-sm px-8 py-4 rounded-full shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95"
          >
            <span>Começar Teste Grátis</span>
            <ArrowRight className="w-4 h-4 text-primary" />
          </Button>
          <a
            href="#pricing"
            className="text-white hover:underline text-sm font-bold flex items-center gap-1 py-2"
          >
            <span>Ver tabela de preços</span>
            <ChevronRight className="w-4 h-4" />
          </a>
        </div>
        <div className="flex flex-wrap justify-center items-center gap-6 pt-4 text-white/70 text-xs font-semibold">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-4 h-4 text-white" /> Sem fidelidade obrigatória
          </span>
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-4 h-4 text-white" /> Ativação instantânea
          </span>
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-4 h-4 text-white" /> Suporte humanizado incluso
          </span>
        </div>
      </div>
    </section>
  );
}
