export interface ChecklistItem {
  id: string;
  text: string;
  completed: boolean;
}

export interface Supplier {
  id: string;
  name: string;
  category: string;
  rating: number;
  avatarUrl?: string;
  isCustom?: boolean;
}

export interface Testimonial {
  id: string;
  name: string;
  role: string;
  text: string;
  rating: number;
  avatarUrl: string;
}

export interface FAQItem {
  id: string;
  question: string;
  answer: string;
}

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

export interface Partner {
  name: string;
  logoUrl: string;
}
