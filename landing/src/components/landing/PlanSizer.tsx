import { useState } from "react";
import { Sparkles, Calendar, Users, HelpCircle, ArrowRight } from "lucide-react";
import { PLANS } from "../../data/landing";
import { Button } from "../ui/button";
import { Slider } from "../ui/slider";
import { Switch } from "../ui/switch";

interface PlanSizerProps {
  onSelectPlan: (planId: string) => void;
}

export function PlanSizer({ onSelectPlan }: PlanSizerProps) {
  const [weddings, setWeddings] = useState<number>(3);
  const [teamSize, setTeamSize] = useState<number>(1);
  const [needsPortal, setNeedsPortal] = useState<boolean>(false);

  let recommendedPlanId = "essential";
  let reason = "Ideal para assessores autônomos que realizam poucos casamentos simultâneos e gerenciam tudo sozinhos.";

  // Thresholds de recomendação de plano:
  // - Enterprise: mais de 15 casamentos/ano OU mais de 5 membros na equipe
  // - Profissional: mais de 3 casamentos/ano OU mais de 1 membro OU precisa de portal de noivos
  // - Essencial: padrão para assessores solo com baixo volume
  if (weddings > 15 || teamSize > 5) {
    recommendedPlanId = "enterprise";
    reason = "Agências de grande porte com equipes robustas e alto volume operacional necessitam do controle absoluto e multi-acesso do plano Enterprise.";
  } else if (weddings > 3 || teamSize > 1 || needsPortal) {
    recommendedPlanId = "professional";
    reason = "Com casamentos múltiplos e colaboradores adicionais, o plano Profissional oferece a automação de checklist e portal de clientes indispensáveis para escalar.";
  }

  const recommendedPlan = PLANS.find((p) => p.id === recommendedPlanId) || PLANS[1];

  return (
    <div className="bg-gradient-to-br from-primary/10 to-transparent p-6 md:p-8 rounded-3xl border border-primary/20 max-w-4xl mx-auto my-12 relative overflow-hidden">
      <div className="absolute top-[-50px] right-[-50px] w-[150px] h-[150px] bg-primary/10 rounded-full blur-2xl"></div>

      <div className="flex flex-col lg:flex-row gap-8 items-center relative z-10">
        <div className="w-full lg:w-1/2 space-y-5">
          <div className="inline-flex items-center gap-1.5 bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 fill-primary" />
            <span>Simulador de Planos</span>
          </div>
          <div>
            <h3 className="text-xl md:text-2xl font-extrabold text-foreground tracking-tight leading-tight">
              Não sabe qual plano escolher?
            </h3>
            <p className="text-sm text-muted-foreground font-medium mt-1">
              Simule sua demanda operacional para descobrir a solução mais rentável para o seu negócio de assessoria.
            </p>
          </div>

          <div className="space-y-4 pt-2">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-foreground flex items-center gap-1.5">
                <Calendar className="w-4 h-4 text-primary" />
                <span>Casamentos ativos por ano: <strong className="text-primary text-sm">{weddings}</strong></span>
              </label>
              <Slider
                min={1}
                max={30}
                step={1}
                value={[weddings]}
                onValueChange={([v]) => setWeddings(v)}
                className="w-full"
              />
              <div className="flex justify-between text-[10px] font-semibold text-muted-foreground/70">
                <span>1 casamento</span>
                <span>15 casamentos</span>
                <span>30+ casamentos</span>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-foreground flex items-center gap-1.5">
                <Users className="w-4 h-4 text-primary" />
                <span>Membros na equipe: <strong className="text-primary text-sm">{teamSize}</strong></span>
              </label>
              <Slider
                min={1}
                max={10}
                step={1}
                value={[teamSize]}
                onValueChange={([v]) => setTeamSize(v)}
                className="w-full"
              />
              <div className="flex justify-between text-[10px] font-semibold text-muted-foreground/70">
                <span>Solo (Eu)</span>
                <span>5 membros</span>
                <span>10+ membros</span>
              </div>
            </div>

            <div className="flex items-center justify-between bg-card/50 backdrop-blur-sm border border-border/20 p-3 rounded-xl">
              <div className="flex items-start gap-2">
                <HelpCircle className="w-4 h-4 text-primary mt-0.5" />
                <div>
                  <p className="text-xs font-bold text-foreground">Portal de Noivos Independente</p>
                  <p className="text-[10px] text-muted-foreground leading-tight">
                    Você quer que os casais acessem checklists e orçamentos diretamente?
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Switch
                  id="needs-portal"
                  checked={needsPortal}
                  onCheckedChange={setNeedsPortal}
                />
                <label htmlFor="needs-portal" className="sr-only cursor-pointer select-none">
                  Portal de Noivos
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className="w-full lg:w-1/2 bg-card rounded-2xl p-6 shadow-xl border border-border/30 text-center flex flex-col items-center gap-4" aria-live="polite">
          <span className="text-[10px] uppercase font-bold tracking-widest text-primary/80 bg-primary/5 px-3 py-1 rounded-full border border-primary/20">
            Recomendação de Especialista
          </span>
          <div>
            <p className="text-xs font-semibold text-muted-foreground">Seu plano ideal é o:</p>
            <h4 className="text-3xl font-black text-primary mt-1">{recommendedPlan.name}</h4>
          </div>

          <p className="text-xs text-muted-foreground leading-relaxed max-w-sm">
            {reason}
          </p>

          <div className="bg-muted border border-border/30 rounded-xl p-3 w-full flex justify-between items-center text-left">
            <div>
              <p className="text-[10px] font-bold text-muted-foreground uppercase">Preço Estimado</p>
              <p className="text-lg font-black text-foreground">R$ {recommendedPlan.monthlyPrice} <span className="text-xs font-normal text-muted-foreground">/mês</span></p>
            </div>
            <span className="text-[10px] text-emerald-600 bg-emerald-50 border border-emerald-100 px-2 py-1 rounded font-bold uppercase">
              14 dias grátis
            </span>
          </div>

          <Button
            onClick={() => onSelectPlan(recommendedPlanId)}
            className="w-full bg-primary hover:bg-primary-hover text-white py-3 rounded-xl font-bold text-sm shadow-md shadow-primary/10 transition-all flex items-center justify-center gap-2 cursor-pointer active:scale-95 duration-150"
          >
            <span>Escolher Plano {recommendedPlan.name}</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
