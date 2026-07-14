import { useState } from "react";
import { ChevronDown, Search, HelpCircle, Send, MessageSquare } from "lucide-react";
import type { FAQItem } from "../../data/types";
import { FAQ_ITEMS, PLANS } from "../../data/landing";
import { Input } from "../ui/input";

export function FAQ() {
  const [faqs] = useState<FAQItem[]>(FAQ_ITEMS);
  const [search, setSearch] = useState("");
  const [openId, setOpenId] = useState<string | null>("faq-1");

  const [userQuestion, setUserQuestion] = useState("");
  const [aiAnswer, setAiAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const toggleAccordion = (id: string) => {
    setOpenId((prev) => (prev === id ? null : id));
  };

  const filteredFaqs = faqs.filter((faq) => {
    return (
      faq.question.toLowerCase().includes(search.toLowerCase()) ||
      faq.answer.toLowerCase().includes(search.toLowerCase())
    );
  });

  const handleAskHelpDesk = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userQuestion.trim()) return;

    setLoading(true);
    setAiAnswer(null);

    setTimeout(() => {
      setLoading(false);
      const q = userQuestion.toLowerCase();
      if (q.includes("whatsapp") || q.includes("contato") || q.includes("comunicação")) {
        setAiAnswer(
          "Sim! O Sim, Aceito! possui integração nativa com o WhatsApp. Você pode enviar lembretes de checklist, confirmações de RSVP e atualizações de orçamentos diretamente para o celular dos noivos ou dos fornecedores com um clique. (Resposta de demonstração)"
        );
      } else if (q.includes("contrato") || q.includes("assinatura") || q.includes("digital")) {
        setAiAnswer(
          "Com certeza. A assinatura digital de contratos está inclusa a partir do plano Profissional. Você e seus fornecedores podem assinar os termos juridicamente válidos diretamente pela plataforma, economizando tempo e papel. (Resposta de demonstração)"
        );
        } else if (q.includes("desconto") || q.includes("anual") || q.includes("pagar")) {
          const discount = Math.round((1 - PLANS[0].annualPrice / PLANS[0].monthlyPrice) * 100);
          setAiAnswer(
            `Oferecemos ${discount}% de desconto no faturamento anual. Você pode assinar via cartão de crédito ou Pix, e cancelar a qualquer momento sem taxas ocultas. (Resposta de demonstração)`
          );
        } else {
          setAiAnswer(
            "Excelente pergunta! Nossa equipe de sucesso do cliente responderá detalhadamente sobre '" +
              userQuestion +
              "' em poucos minutos. Como você está em nosso ambiente de demonstração, sinta-se à vontade para testar as ferramentas de checklist e dashboard financeiro ao lado!"
          );
        }
      }, 1200);
  };

  return (
    <section id="faq" className="py-20 md:py-28 relative z-10 bg-white border-t border-border/20">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <span className="text-xs font-bold text-primary uppercase tracking-widest bg-primary/5 px-4 py-1.5 rounded-full">
            Dúvidas
          </span>
          <h2 className="text-3xl md:text-4xl font-black text-foreground tracking-tight">Dúvidas Frequentes</h2>
          <p className="text-base text-muted-foreground font-medium leading-relaxed">
            Tudo o que você precisa saber sobre como a Sim, Aceito! pode transformar a gestão da sua assessoria de casamentos.
          </p>
        </div>

        <div className="max-w-3xl mx-auto space-y-6">
          <div className="relative">
            <Search className="absolute left-4 top-3 w-5 h-5 text-muted-foreground/40" />
            <Input
              type="text"
              placeholder="Busque por termos (ex: despesa, parcelamento, testar, relatórios)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-white text-sm py-3.5 pl-12 pr-6 rounded-2xl border border-border/50 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all text-foreground placeholder:text-muted-foreground/40 shadow-sm"
            />
          </div>

          <div className="space-y-4">
            {filteredFaqs.map((faq) => {
              const isOpen = openId === faq.id;
              return (
                <div
                  key={faq.id}
                  className="bg-white rounded-2xl border border-border/30 shadow-sm overflow-hidden transition-all duration-300 hover:shadow-md"
                >
                  <button
                    onClick={() => toggleAccordion(faq.id)}
                    className="w-full text-left px-6 py-5 flex justify-between items-center group focus:outline-none cursor-pointer"
                  >
                    <span className={`font-bold text-base md:text-lg transition-colors duration-200 ${isOpen ? "text-primary" : "text-foreground group-hover:text-primary"}`}>
                      {faq.question}
                    </span>
                    <ChevronDown
                      className={`w-5 h-5 text-muted-foreground transition-transform duration-300 ${
                        isOpen ? "rotate-180 text-primary" : "group-hover:text-primary"
                      }`}
                    />
                  </button>

                  <div
                    className={`transition-all duration-300 ease-in-out px-6 ${
                      isOpen ? "pb-6 max-h-[1000px] opacity-100" : "max-h-0 opacity-0 pointer-events-none"
                    }`}
                  >
                    <p className="text-sm md:text-base text-muted-foreground leading-relaxed">
                      {faq.answer}
                    </p>
                  </div>
                </div>
              );
            })}

            {filteredFaqs.length === 0 && (
              <p className="text-center py-8 text-muted-foreground font-semibold">
                Nenhuma dúvida encontrada para "{search}". Tente buscar por outros termos!
              </p>
            )}
          </div>

          <div className="bg-primary/5 rounded-3xl p-6 border border-primary/10 mt-10">
            <div className="flex items-start gap-3 mb-4">
              <HelpCircle className="w-5 h-5 text-primary mt-0.5" />
              <div>
                <h4 className="font-bold text-sm text-foreground">Ainda com dúvidas? Pergunte ao assistente!</h4>
                <p className="text-xs text-muted-foreground">Temos respostas instantâneas para perguntas sobre WhatsApp, contratos e assinaturas.</p>
              </div>
            </div>

            <form onSubmit={handleAskHelpDesk} className="relative flex items-center">
              <Input
                type="text"
                placeholder="Digite sua dúvida aqui..."
                value={userQuestion}
                onChange={(e) => setUserQuestion(e.target.value)}
                className="w-full pl-4 pr-12 py-3 bg-white border border-border/50 rounded-xl text-xs focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary text-foreground placeholder:text-muted-foreground/40 shadow-sm"
              />
              <button
                type="submit"
                className="absolute right-1.5 p-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors cursor-pointer"
                aria-label="Enviar pergunta"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>

            {loading && (
              <div className="flex items-center gap-2 text-xs font-semibold text-primary mt-3 animate-soft-pulse">
                <span className="w-2 h-2 rounded-full bg-primary animate-bounce"></span>
                <span className="w-2 h-2 rounded-full bg-primary animate-bounce delay-100"></span>
                <span className="w-2 h-2 rounded-full bg-primary animate-bounce delay-200"></span>
                <span>Digitando resposta...</span>
              </div>
            )}

            {aiAnswer && (
              <div className="bg-white p-4 rounded-2xl border border-primary/10 text-xs text-muted-foreground leading-relaxed shadow-sm mt-3 animate-in fade-in duration-300 flex gap-2.5 items-start">
                <MessageSquare className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                <span>{aiAnswer}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
