import { FinancialDashboardCard } from "./FinancialDashboardCard";
import { ChecklistCard } from "./ChecklistCard";
import { SuppliersCard } from "./SuppliersCard";
import { INITIAL_CHECKLIST, INITIAL_SUPPLIERS } from "../../data/landing";

export function Features() {
  return (
    <section id="features" className="py-20 md:py-28 border-t border-border/20 relative z-10 bg-card">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-bold text-primary uppercase tracking-widest bg-primary/5 px-4 py-1.5 rounded-full">
            Tudo o que você precisa em um só lugar
          </span>
          <h2 className="text-3xl md:text-4xl font-black text-foreground tracking-tight">
            A melhor experiência para gerenciar seus casamentos
          </h2>
          <p className="text-base text-muted-foreground font-medium leading-relaxed">
            Integre suas operações e dê adeus às planilhas obsoletas. Teste as ferramentas interativas de simulação abaixo!
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
          <FinancialDashboardCard />
          <ChecklistCard initialItems={INITIAL_CHECKLIST} />
          <SuppliersCard initialItems={INITIAL_SUPPLIERS} />
        </div>
      </div>
    </section>
  );
}
