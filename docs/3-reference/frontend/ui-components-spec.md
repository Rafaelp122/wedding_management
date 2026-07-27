# Especificação Técnica: Componentes de UI (shadcn/ui & Tailwind CSS)

> **Módulo:** [frontend-reference](index.md) | [smart-dumb-components](../../4-explanation/architecture/smart-dumb-components.md)
> **Camada:** Frontend (`frontend/src/components/ui/`, `frontend/src/components/`)

---

## Visão Geral

A interface do **Wedding Management System** é construída com **React 18/19**, **TypeScript**, **Tailwind CSS (v4)** e **shadcn/ui**.

---

## Componentes de Infraestrutura (`src/components/ui/`)

Os componentes base shadcn/ui são agnósticos ao domínio e residem na pasta `src/components/ui/`. ELES NÃO DEVEM conter regras de negócio.

| Componente | Função | Padrões de Acessibilidade |
| :--- | :--- | :--- |
| `Button` | Ações principais e secundárias | Suporte a variantes (`default`, `destructive`, `outline`, `ghost`), estados de `loading`. |
| `Dialog` / `Sheet` | Modais e gavetas laterais | Obrigatoriamente possui `DialogTitle` e `DialogDescription` para WCAG/a11y. |
| `Form` / `Input` | Campos de formulário controlados | Integração direta com `react-hook-form` e `zodResolver`. |
| `Table` | Exibição tabulada de dados | Suporte a cabeçalhos acessíveis, linhas selecionáveis e ordenação. |
| `Toast` / `Sonner` | Notificações do sistema | Disparado via `toast.success()`, `toast.error()`. |

---

## Padrão de Composição e Customização

- Não altere diretamente a estrutura base de `src/components/ui/`.
- Crie componentes de negócio compondo os elementos primitivos shadcn/ui dentro da respectiva feature em `src/features/<modulo>/components/`.
- Use a utilidade `cn()` de `@/lib/utils` para mesclar classes Tailwind condicionalmente.
