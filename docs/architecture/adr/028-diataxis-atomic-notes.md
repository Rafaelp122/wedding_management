# ADR-028: Adoção do Framework Diatáxis e Padrão de Anotações Atômicas na Documentação

**Status:** Aceito
**Data:** 2026-08-08
**Módulo:** Documentação e Governança

---

## 1. Contexto e Problema

O projeto cresceu substancialmente, englobando integrações fullstack (Django Ninja, React, Orval, R2, Cloud Run, Neon). Durante esse crescimento inicial, as documentações se tornaram monolíticas, difíceis de ler e misturavam explicações teóricas abstratas com comandos de terminal pontuais.

Isso prejudicava a curva de aprendizado de novos desenvolvedores (onboarding) e dificultava encontrar respostas rápidas durante a manutenção do código ou na resolução de incidentes.

---

## 2. Decisão

Adotamos duas diretrizes rigorosas para governar o ciclo de vida de todo o conhecimento escrito da plataforma:

1. **Framework Diatáxis:** Toda documentação oficial deve ser alocada estritamente em um dos 4 quadrantes definidos pelo framework, correspondentes aos subdiretórios em `docs/`:
   - `onboarding/`: Para ensino e onboarding. Orientado ao aprendizado prático passo a passo.
   - `guides/`: Receitas para resolver um problema pontual do dia a dia. Orientado a tarefas.
   - `reference/`: Especificações técnicas de schemas, classes, modelos e dados secos.
   - `architecture/`: Porquês arquiteturais, regras de negócios atômicas e ADRs.
2. **Anotações Atômicas (Atomic Notes):** Cada documento no repositório não deve exceder um único escopo de conceito ou regra de negócio. Se um arquivo começar a cruzar múltiplos assuntos ou for maior que ~250 linhas, ele deve ser desmembrado.
   - _Regra semântica:_ Um documento atômico deve ter **somente um cabeçalho H1 (`#`)**.
   - _On-demand Skills:_ Skills em `.agents/skills/` atuam como checklists operacionais enxutos que apontam para as notas atômicas em `docs/`.

---

## 3. Consequências

**Positivas:**

- Reduz carga cognitiva: desenvolvedores com dúvidas práticas sabem que não precisam ler explicações conceituais da pasta `architecture/`.
- Promove a reutilização: anotações atômicas podem ser linkadas livremente entre si criando uma rede de conhecimento orgânica (estilo _Zettelkasten_).
- Otimização de contexto para agentes de IA: subagentes e a IA revisora leem apenas a nota atômica relevante ao `git diff`, economizando tokens e eliminando alucinações.

**Negativas / Trade-offs:**

- Um maior número de arquivos pequenos e granulares. Desenvolvedores utilizam os índices `docs/index.md` e `docs/architecture/adr/README.md` ou a busca da IDE (`grep`) para navegação.
