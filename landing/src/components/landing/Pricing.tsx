import { useState } from "react";
import { Check } from "lucide-react";
import { PLANS } from "../../data/landing";
import { PlanSizer } from "./PlanSizer";
import { Button } from "../ui/button";
import { Card } from "../ui/card";

interface PricingProps {
  onOpenLead: () => void;
}

export function Pricing({ onOpenLead }: PricingProps) {
  const [annualBilling, setAnnualBilling] = useState(false);

  const annualBillingDiscount = Math.round(
    (1 - PLANS[0].annualPrice / PLANS[0].monthlyPrice) * 100
  );

  return (
    <section id="pricing" className="py-20 md:py-28 relative z-10 bg-background">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="text-center max-w-3xl mx-auto mb-10 space-y-4">
          <span className="text-xs font-bold text-primary uppercase tracking-widest bg-primary/5 px-4 py-1.5 rounded-full">
            Investimento
          </span>
          <h2 className="text-3xl md:text-4xl font-black text-foreground tracking-tight">
            O investimento que cresce com você
          </h2>
          <p className="text-base text-muted-foreground font-medium leading-relaxed">
            Planos transparentes e flexíveis para assessorias de todos os tamanhos. Comece hoje com 14 dias grátis.
          </p>

          <div className="inline-flex items-center justify-center p-1 bg-card border border-border rounded-full mt-4 shadow-sm">
            <button
              onClick={() => setAnnualBilling(false)}
              className={`px-5 py-2 rounded-full text-xs font-bold transition-all cursor-pointer ${
                !annualBilling ? "bg-primary text-white shadow-sm" : "text-muted-foreground hover:text-primary"
              }`}
            >
              Mensal
            </button>
            <button
              onClick={() => setAnnualBilling(true)}
              className={`px-5 py-2 rounded-full text-xs font-bold transition-all cursor-pointer flex items-center gap-1 ${
                annualBilling ? "bg-primary text-white shadow-sm" : "text-muted-foreground hover:text-primary"
              }`}
            >
              <span>Anual</span>
              <span className={`text-[9px] font-black uppercase px-1.5 py-0.5 rounded-full ${annualBilling ? "bg-white text-primary" : "bg-primary/10 text-primary"}`}>
                -{annualBillingDiscount}%
              </span>
            </button>
          </div>
        </div>

        <PlanSizer onSelectPlan={(planId: string) => onOpenLead()} />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch pt-8">
          {PLANS.map((plan) => {
            const price = annualBilling ? plan.annualPrice : plan.monthlyPrice;
  const annualBillingDiscount = Math.round(
    (1 - PLANS[0].annualPrice / PLANS[0].monthlyPrice) * 100
  );

  return (
              <Card
                key={plan.id}
                className={`bg-card rounded-3xl p-8 border hover:shadow-xl transition-all duration-300 relative flex flex-col justify-between h-full overflow-visible ${
                  plan.isPopular
                    ? "border-2 border-primary shadow-xl scale-[1.02] md:translate-y-[-10px] z-10"
                    : "border-border/50"
                }`}
              >
                {plan.isPopular && (
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 -mt-3.5 bg-primary text-white px-4 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-widest shadow-md z-20">
                    Mais Escolhido
                  </div>
                )}

                <div>
                  <h3 className="text-xl font-black text-foreground mb-1.5">{plan.name}</h3>
                  <p className="text-xs text-muted-foreground leading-relaxed mb-6 font-medium">{plan.description}</p>

                  <div className="flex items-baseline gap-1 mb-6">
                    <span className="text-4xl font-black text-foreground">R$ {price}</span>
                    <span className="text-xs text-muted-foreground font-medium">/mês</span>
                  </div>

                  <ul className="space-y-3.5 mb-8">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2.5 text-xs md:text-sm text-muted-foreground">
                        <Check className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                        <span className="font-medium">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={onOpenLead}
                  className={`w-full py-3.5 rounded-xl font-extrabold text-xs tracking-wider uppercase transition-all cursor-pointer active:scale-95 ${
                    plan.isPopular
                      ? "bg-primary text-white hover:bg-primary-hover shadow-lg shadow-primary/20"
                      : "border border-border hover:bg-primary/5 hover:text-primary text-foreground"
                  }`}
                >
                  {plan.buttonText}
                </button>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}
