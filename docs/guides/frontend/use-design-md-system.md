# How-To: Como Usar, Validar e Exportar o Design System (`DESIGN.md`)

Este guia prático explica como manter, validar via CLI e exportar os tokens de design do [DESIGN.md](../../../DESIGN.md) para o **Tailwind CSS v4** e componentes do frontend.

> **Módulo:** [design-system-rationale](../../architecture/concepts/design-system-rationale.md) | [ui-components-spec](../../reference/frontend/ui-components-spec.md)
> **Arquivo de Tokens:** `DESIGN.md` (na raiz do repositório)

---

## 1. Estrutura de Camadas do `DESIGN.md`

O `DESIGN.md` é dividido em duas camadas:
1. **YAML Frontmatter (Tokens Normativos):** Especificação em código parseável por agentes de IA e ferramentas de CLI.
2. **Body Markdown (Prosa e Contexto):** Explicação em 8 seções padrão (`Overview`, `Colors`, `Typography`, `Layout`, `Elevation & Depth`, `Shapes`, `Components`, `Do's and Don'ts`).

---

## 2. Validação e Linting via CLI (`@google/design.md`)

Para garantir que novos tokens não quebrem regras de contraste WCAG AA ou tenham referências inválidas, execute o linter oficial do Google:

```bash
# Validar estrutura, referências e contraste WCAG AA
npx -y @google/design.md lint DESIGN.md
```

Ou execute a checagem completa da documentação que já inclui o linter:

```bash
just check-docs
```

---

## 3. Exportação de Tokens para Tailwind CSS v4

Os tokens definidos no `DESIGN.md` podem ser exportados diretamente para CSS compatível com o bloco `@theme` do **Tailwind CSS v4**:

```bash
# Gerar bloco CSS @theme com variáveis nativas
npx -y @google/design.md export --format css-tailwind DESIGN.md
```

### Exemplo de Saída Exportada:
```css
@theme {
  --color-primary: #7C3AED;
  --color-secondary: #F5F3FF;
  --color-surface: #FAFAFB;
  --font-display: "Plus Jakarta Sans Variable";
  --font-sans: "IBM Plex Sans Variable";
  --font-mono: "JetBrains Mono Variable";
  --radius-md: 8px;
}
```

---

## 4. Regras de Composição de Componentes (`shadcn/ui` + Tailwind v4)

- **Nunca edite arquivos em `src/components/ui/`:** Os componentes base do shadcn são imutáveis.
- **Estilização por Composição:** Aplique variações visuais no componente da feature usando utilitários do Tailwind:
  ```tsx
  // CORRETO — Composição com utilitários Tailwind baseados nos tokens
  <Card className="bg-surface border-border p-6 rounded-lg">
    <CardHeader>
      <CardTitle className="font-display text-xl text-foreground">Título</CardTitle>
    </CardHeader>
  </Card>
  ```
- **Proibido Estilos Inline:** Nunca utilize `style={{ ... }}`. Use sempre as classes utilitárias ou variáveis registradas no `@theme inline`.
