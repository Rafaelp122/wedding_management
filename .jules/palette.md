## 2025-05-15 - [Acessibilidade em Inputs de Senha]
**Learning:** Elementos interativos apenas com ícones (como o alternador de visibilidade de senha) frequentemente são ignorados na acessibilidade. A remoção de `tabIndex={-1}` aliada a `aria-label` dinâmicos e Tooltips é essencial para garantir que usuários de teclado e leitores de tela tenham a mesma experiência. Além disso, o `TooltipProvider` deve estar no nível global (App e TestUtils) para evitar erros de contexto do Radix UI.
**Action:** Sempre que adicionar um botão de ícone, verificar se ele possui `aria-label`, se é focável via teclado e se possui uma dica visual (Tooltip).

## 2025-05-15 - [Padronização de Props em Componentes de UI]
**Learning:** Ao criar componentes que envolvem elementos nativos do HTML (como inputs), deve-se sempre estender `React.ComponentPropsWithoutRef<"elemento">` em vez de criar uma interface manual limitada. Isso garante que o componente suporte todas as props padrão (id, name, value, handlers, etc.) e siga as convenções do ecossistema React.
**Action:** Usar `extends React.ComponentPropsWithoutRef<...>` em componentes base de UI.

## 2025-05-15 - [Testando Tooltips do Radix UI em Vitest]
**Learning:** Testar tooltips do Radix UI requer atenção à natureza assíncrona do componente e ao atraso (delay) padrão. Configurar o `TooltipProvider` com `delayDuration={0}` no wrapper de testes e utilizar `waitFor` junto com queries semânticas (`screen.getByRole('tooltip', { name: '...' })`) garante testes robustos e confiáveis, evitando falsos negativos e garantindo que o conteúdo esteja de fato acessível ao usuário.
**Action:** Configurar `delayDuration={0}` no `TooltipProvider` de teste e usar `waitFor` com `getByRole('tooltip', ...)` para verificar tooltips.
