# ADR-028: Adoção do Framework Diatáxis e Padrão de Anotações Atômicas na Documentação

**Status:** Aceito
**Data:** 2024-06-13 (Formalizado em 2026-08-08)
**Módulo:** Documentação e Governança

---

## 1. Contexto e Problema

O projeto cresceu substancialmente, englobando integrações fullstack (Django Ninja, React, Orval, R2, Cloud Run, Neon). Durante esse crescimento inicial, as documentações se tornaram monolíticas, difíceis de ler e misturavam explicações teóricas abstratas com comandos de terminal pontuais.

Isso prejudicava a curva de aprendizado de novos desenvolvedores (onboarding) e dificultava encontrar respostas rápidas durante a manutenção do código ou na resolução de incidentes.

---

## 2. Decisão

Adotamos duas diretrizes rigorosas para governar o ciclo de vida de todo o conhecimento escrito da plataforma:

1. **Framework Diatáxis:** Toda documentação oficial deve ser alocada estritamente em um dos 4 quadrantes definidos pelo framework, correspondentes aos subdiretórios em `docs/`:
   - `1-tutorials/`: Para ensino e onboarding. Orientado ao aprendizado prático passo a passo.
   - `2-how-to/`: Receitas para resolver um problema pontual do dia a dia. Orientado a tarefas.
   - `3-reference/`: Especificações técnicas de schemas, classes, modelos e dados secos.
   - `4-explanation/`: Porquês arquiteturais, regras de negócios atômicas e ADRs.
2. **Anotações Atômicas (Atomic Notes):** Cada documento no repositório não deve exceder um único escopo de conceito ou regra de negócio. Se um arquivo começar a cruzar múltiplos assuntos ou for maior que ~250 linhas, ele deve ser desmembrado.
   - *Regra semântica:* Um documento atômico deve ter **somente um cabeçalho H1 (`#`)**.
   - *On-demand Skills:* Skills em `.agents/skills/` atuam como checklists operacionais enxutos que apontam para as notas atômicas em `docs/`.

---

## 3. Consequências

**Positivas:**
- Reduz carga cognitiva: desenvolvedores com dúvidas práticas sabem que não precisam ler explicações conceituais da pasta `4-explanation/`.
- Promove a reutilização: anotações atômicas podem ser linkadas livremente entre si criando uma rede de conhecimento orgânica (estilo *Zettelkasten*).
- Otimização de contexto para agentes de IA: subagentes e a IA revisora leem apenas a nota atômica relevante ao `git diff`, economizando tokens e eliminando alucinações.

**Negativas / Trade-offs:**
- Um maior número de arquivos pequenos e granulares. Desenvolvedores utilizam os índices `docs/README.md` e `docs/4-explanation/adr/README.md` ou a busca da IDE (`grep`) para navegação.
