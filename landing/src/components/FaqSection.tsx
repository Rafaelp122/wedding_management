import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';

export default function FaqSection() {
  return (
    <div className="w-full space-y-4 text-left">
      <Accordion type="single" collapsible className="w-full space-y-4">
        <AccordionItem
          value="item-1"
          className="p-1 px-4 bg-white dark:bg-surface-darkSecondary rounded-xl border border-zinc-200/80 dark:border-zinc-800"
        >
          <AccordionTrigger className="font-display font-bold text-sm text-zinc-950 dark:text-white hover:no-underline">
            Como funciona o parcelamento automático?
          </AccordionTrigger>
          <AccordionContent className="text-xs text-zinc-550 dark:text-zinc-400 leading-relaxed pt-2">
            Sempre que lança um contrato de fornecedor, pode escolher o número de faturas e o primeiro vencimento. O Sim, Aceito! ERP gera as parcelas sequenciais automaticamente no calendário financeiro para não ter de lançar uma a uma.
          </AccordionContent>
        </AccordionItem>

        <AccordionItem
          value="item-2"
          className="p-1 px-4 bg-white dark:bg-surface-darkSecondary rounded-xl border border-zinc-200/80 dark:border-zinc-800"
        >
          <AccordionTrigger className="font-display font-bold text-sm text-zinc-950 dark:text-white hover:no-underline">
            Posso compartilhar as despesas diretamente com os noivos?
          </AccordionTrigger>
          <AccordionContent className="text-xs text-zinc-550 dark:text-zinc-400 leading-relaxed pt-2">
            Sim! Através da ferramenta de relatórios de um clique, pode gerar um resumo de fluxo de caixa limpo em formato PDF para que os noivos visualizem os pagamentos em dia de forma transparente.
          </AccordionContent>
        </AccordionItem>

        <AccordionItem
          value="item-3"
          className="p-1 px-4 bg-white dark:bg-surface-darkSecondary rounded-xl border border-zinc-200/80 dark:border-zinc-800"
        >
          <AccordionTrigger className="font-display font-bold text-sm text-zinc-950 dark:text-white hover:no-underline">
            Preciso pagar para testar?
          </AccordionTrigger>
          <AccordionContent className="text-xs text-zinc-550 dark:text-zinc-400 leading-relaxed pt-2">
            Não. Ao criar a sua conta hoje, recebe 14 dias de teste totalmente gratuito com todas as funcionalidades operacionais liberadas para testar com os seus casamentos reais.
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
