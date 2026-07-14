import type { ChecklistItem, Supplier, Testimonial, FAQItem, Plan, Partner } from "./types";

export const INITIAL_CHECKLIST: ChecklistItem[] = [
  { id: "1", text: "Confirmar fornecedores", completed: true },
  { id: "2", text: "Reunião final com casal", completed: false },
  { id: "3", text: "Enviar cronograma", completed: false },
  { id: "4", text: "Definir mapa de mesas", completed: false },
  { id: "5", text: "Contratar gerador de energia", completed: true }
];

export const INITIAL_SUPPLIERS: Supplier[] = [
  {
    id: "1",
    name: "Studio Luz",
    category: "Fotografia",
    rating: 5.0,
    avatarUrl: "https://i.pravatar.cc/150?img=12"
  },
  {
    id: "2",
    name: "Doce Sonho",
    category: "Confeitaria",
    rating: 4.9,
    avatarUrl: "https://i.pravatar.cc/150?img=25"
  }
];

export const TESTIMONIALS: Testimonial[] = [
  {
    id: "1",
    name: "Ana Clara Fontes",
    role: "Cerimonialista Sênior",
    text: "A plataforma mudou completamente a forma como organizo os eventos. O dashboard financeiro é incrivelmente intuitivo e me dá a tranquilidade que eu precisava para focar no que realmente importa: encantar meus noivos.",
    rating: 5,
    avatarUrl: "https://i.pravatar.cc/150?img=32"
  },
  {
    id: "2",
    name: "Carlos Eduardo",
    role: "Fundador, CE Eventos",
    text: "Ter todas as informações centralizadas reduziu nossa margem de erro a zero. A funcionalidade de checklists compartilhados com os clientes transmite um nível de profissionalismo que virou nosso diferencial.",
    rating: 5,
    avatarUrl: "https://i.pravatar.cc/150?img=33"
  },
  {
    id: "3",
    name: "Beatriz Lima",
    role: "Assessora de Casamentos",
    text: "Eu costumava usar dezenas de planilhas. Com o Sim, Aceito!, ganhei horas no meu dia e uma visão clara do fluxo de caixa da agência. O design é lindo e o suporte é excepcional.",
    rating: 4.5,
    avatarUrl: "https://i.pravatar.cc/150?img=47"
  }
];

export const FAQ_ITEMS: FAQItem[] = [
  {
    id: "faq-1",
    question: "Posso compartilhar despesas?",
    answer: "Sim! Nosso sistema permite que você divida as despesas entre os noivos, familiares ou padrinhos, gerando relatórios de pagamento individuais e links de cobrança separados, tudo de forma transparente e organizada no dashboard financeiro do casal."
  },
  {
    id: "faq-2",
    question: "Como funciona o parcelamento?",
    answer: "Você pode configurar planos de pagamento flexíveis para seus clientes. O sistema calcula automaticamente as parcelas, envia lembretes de vencimento integrados ao WhatsApp e e-mail, e atualiza o status do dashboard financeiro assim que o pagamento for confirmado."
  },
  {
    id: "faq-3",
    question: "Preciso pagar para testar?",
    answer: "Não. Oferecemos 14 dias de teste totalmente gratuito, sem necessidade de cadastrar cartão de crédito. Você terá acesso completo a todas as funcionalidades premium, incluindo gestão de contratos, controle financeiro e RSVP online, para avaliar se o Sim, Aceito! é a solução ideal para o seu negócio."
  },
  {
    id: "faq-4",
    question: "Consigo exportar relatórios em PDF/Excel?",
    answer: "Com certeza! Todos os dados financeiros, cronogramas de eventos e diretórios de fornecedores podem ser exportados em relatórios profissionais em PDF ou planilhas Excel com apenas um clique, perfeitos para enviar aos noivos ou prestadores de serviços."
  },
  {
    id: "faq-5",
    question: "O acesso para os noivos é pago à parte?",
    answer: "Não. No plano Profissional e Enterprise, o acesso dos noivos (Portal do Cliente) está totalmente incluso, sem limite de casais ativos. Você pode convidá-los e colaborar de forma integrada."
  }
];

export const PLANS: Plan[] = [
  {
    id: "essential",
    name: "Essencial",
    description: "Para quem está começando a organizar os primeiros eventos.",
    monthlyPrice: 97,
    annualPrice: 77,
    features: [
      "Até 3 casamentos ativos",
      "Checklist padrão",
      "Gestão financeira básica",
      "Modelos de contratos",
      "Suporte por e-mail"
    ],
    buttonText: "Começar Agora"
  },
  {
    id: "professional",
    name: "Profissional",
    description: "O plano completo para assessorias consolidadas no mercado.",
    monthlyPrice: 297,
    annualPrice: 237,
    features: [
      "Casamentos ilimitados",
      "Portal do cliente (Noivos)",
      "Controle financeiro avançado",
      "Assinatura digital de contratos",
      "RSVP Integrado com WhatsApp",
      "Suporte prioritário via chat"
    ],
    isPopular: true,
    buttonText: "Começar Agora"
  },
  {
    id: "enterprise",
    name: "Enterprise",
    description: "Para agências com múltiplas equipes e alto volume.",
    monthlyPrice: 597,
    annualPrice: 477,
    features: [
      "Tudo do plano Profissional",
      "Múltiplos usuários com permissões",
      "Relatórios personalizados",
      "Suporte prioritário 24/7",
      "Treinamento de equipe dedicado",
      "Domínio personalizado (White-label)"
    ],
    buttonText: "Falar com Vendas"
  }
];

export const PARTNERS: Partner[] = [
  {
    name: "Revista Casar",
    logoUrl: "https://logodownload.org/wp-content/uploads/2014/04/revista-casar-logo-1.png"
  },
  {
    name: "zankyou",
    logoUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Zankyou_logo.svg/200px-Zankyou_logo.svg.png"
  },
  {
    name: "Bride's Magazine",
    logoUrl: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Brides_magazine_logo.svg/200px-Brides_magazine_logo.svg.png"
  },
  {
    name: "WeddingPlanner Pro",
    logoUrl: "https://via.placeholder.com/120x40/630ed4/ffffff?text=WPP"
  }
];
