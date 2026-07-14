/** Item de checklist com estado de conclusão. */
export interface ChecklistItem {
  id: string;
  text: string;
  completed: boolean;
}

/** Fornecedor do diretório de parceiros recomendados. */
export interface Supplier {
  id: string;
  name: string;
  category: string;
  rating: number;
  avatarUrl?: string;
  isCustom?: boolean;
}

/** Depoimento de cliente exibido na seção de casos de sucesso. */
export interface Testimonial {
  id: string;
  name: string;
  role: string;
  text: string;
  rating: number;
  avatarUrl: string;
}

/** Item de FAQ com pergunta e resposta. */
export interface FAQItem {
  id: string;
  question: string;
  answer: string;
}

/** Plano de assinatura com preços mensal e anual. */
export interface Plan {
  id: string;
  name: string;
  description: string;
  monthlyPrice: number;
  annualPrice: number;
  features: string[];
  isPopular?: boolean;
  buttonText: string;
}

/** Parceiro institucional com logo. */
export interface Partner {
  name: string;
  logoUrl: string;
}
