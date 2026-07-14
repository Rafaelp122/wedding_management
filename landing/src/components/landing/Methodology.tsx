import { useState } from "react";
import { Calendar, Check, Award, ArrowRight } from "lucide-react";
import { Button } from "../ui/button";

interface MethodologyProps {
  onOpenLead: () => void;
}

const steps = [
  {
    id: 1,
    icon: Calendar,
    title: "Planejamento",
    shortDesc: "Gestão de agenda, centralização de contratos e orçamentos iniciais em um ambiente unificado.",
    fullTitle: "Fase 1: Captação, Cronogramas e Orçamentos",
    fullDesc: "Inicie organizando as expectativas do casal. Configure o orçamento global limite, elabore o primeiro checklist automatizado de 12 meses e convide os noivos para colaborar no painel."
  },
  {
    id: 2,
    icon: Check,
    title: "Execução",
    shortDesc: "Acompanhamento de checklists, gestão de fornecedores e comunicação em tempo real com o casal.",
    fullTitle: "Fase 2: Conciliação, RSVP e Checklists Inteligentes",
    fullDesc: "Conforme o casamento se aproxima, monitore as parcelas pendentes dos noivos, coordene a entrega com fornecedores qualificados e libere a confirmação de RSVP online via WhatsApp."
  },
  {
    id: 3,
    icon: Award,
    title: "Fechamento",
    shortDesc: "Conciliação financeira automática, relatórios de rentabilidade e pesquisa de satisfação final.",
    fullTitle: "Fase 3: Entrega, Retorno Financeiro e Fidelização",
    fullDesc: "Após o brinde do casal, realize a conciliação final do caixa, arquive o histórico completo de fornecedores acionados e envie um formulário automatizado para registrar o depoimento de satisfação."
  }
];

export function Methodology({ onOpenLead }: MethodologyProps) {
  const [processStep, setProcessStep] = useState(1);

  const activeStep = steps.find(s => s.id === processStep) || steps[0];

  return (
    <section id="process" className="py-20 md:py-28 relative z-10 bg-gradient-to-b from-card to-background">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-bold text-primary uppercase tracking-widest bg-primary/5 px-4 py-1.5 rounded-full">
            Metodologia Operacional
          </span>
          <h2 className="text-3xl md:text-4xl font-black text-foreground tracking-tight">
            Segurança operacional para múltiplos eventos
          </h2>
          <p className="text-base text-muted-foreground font-medium leading-relaxed">
            Controle total de cada etapa. Do primeiro contato ao brinde final, nosso fluxo garante que nada passe despercebido, mesmo com dezenas de casamentos simultâneos.
          </p>
        </div>

        <div className="relative max-w-5xl mx-auto mt-12">
          <div className="hidden md:block absolute top-[45px] left-[15%] right-[15%] h-[2px] bg-border/40 z-0"></div>

          <div className="flex flex-col md:flex-row justify-between items-start gap-12 md:gap-8 relative z-10">
            {steps.map((step) => {
              const Icon = step.icon;
              return (
                <button
                  key={step.id}
                  onClick={() => setProcessStep(step.id)}
                  className="flex-1 flex flex-col items-center text-center group focus:outline-none"
                >
                  <div
                    className={`w-[90px] h-[90px] rounded-full flex items-center justify-center mb-5 relative transition-all duration-300 border-2 cursor-pointer ${
                      processStep === step.id
                        ? "bg-card shadow-xl scale-105 border-primary"
                        : "bg-muted border-border/30 group-hover:-translate-y-1.5 hover:shadow-lg"
                    }`}
                  >
                    <div className="absolute -top-1.5 -right-1.5 w-7 h-7 rounded-full bg-primary text-white flex items-center justify-center text-xs font-black shadow-md">
                      {step.id}
                    </div>
                    <Icon className={`w-8 h-8 ${processStep === step.id ? "text-primary" : "text-muted-foreground"}`} />
                  </div>
                  <h3 className={`font-black text-lg ${processStep === step.id ? "text-primary" : "text-foreground"}`}>
                    {step.title}
                  </h3>
                  <p className="text-xs text-muted-foreground font-medium mt-2 max-w-xs leading-relaxed">
                    {step.shortDesc}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        <div className="mt-16 bg-card rounded-3xl p-6 md:p-8 border border-border/30 shadow-lg max-w-3xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="space-y-1.5 text-center md:text-left">
            <p className="text-xs font-bold uppercase tracking-wider text-primary">
              Visualizando detalhe de: {activeStep.title}
            </p>
            <h4 className="text-lg md:text-xl font-black text-foreground">
              {activeStep.fullTitle}
            </h4>
            <p className="text-xs text-muted-foreground max-w-md font-medium leading-relaxed">
              {activeStep.fullDesc}
            </p>
          </div>
          <Button
            onClick={onOpenLead}
            className="bg-primary hover:bg-primary-hover text-white text-xs font-extrabold px-6 py-3 rounded-xl transition-all shadow-md shadow-primary/10 flex items-center gap-2 whitespace-nowrap shrink-0 cursor-pointer"
          >
            <span>Conhecer Metodologia Completa</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </section>
  );
}
