import { CheckCircle2 } from "lucide-react";

const features = [
  { title: "Controle Financeiro", desc: "Gestão de pagamentos em tempo real." },
  { title: "Scheduler Inteligente", desc: "Cronogramas automatizados." },
  { title: "Gestão de Itens", desc: "Inventário completo de logística." },
];

export function FeaturesSection() {
  return (
    <section className="container py-12 md:py-24 lg:py-32 mx-auto px-4 md:px-6">
      <div className="grid gap-8 md:grid-cols-3">
        {features.map((f, i) => (
          <div
            key={i}
            className="flex flex-col items-center p-6 border rounded-xl bg-card shadow-sm"
          >
            <CheckCircle2 className="h-10 w-10 text-pink-500 mb-4" />
            <h3 className="text-xl font-bold mb-2">{f.title}</h3>
            <p className="text-muted-foreground text-center">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
