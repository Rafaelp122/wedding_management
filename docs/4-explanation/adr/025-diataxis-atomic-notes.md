# ADR-025: Adoção do Framework Diatáxis e Padrão de Anotações Atômicas na Documentação

**Status:** Aceito
**Data:** 2024-06-13
**Módulo:** Documentação e Governança

## 1. Contexto e Problema

O projeto tem crescido substancialmente, englobando integrações fullstack (Django, React, Orval, R2, Cloud Run, Neon). Durante esse crescimento, as documentações (READMEs e guias) se tornaram monolíticas, difíceis de ler e misturavam explicações teóricas abstratas com comandos de terminal pontuais.

Isso prejudica a curva de aprendizado de novos desenvolvedores (onboarding) e dificulta encontrar respostas rápidas durante a manutenção do código ou na resolução de incidentes.

## 2. Decisão

Adotamos duas diretrizes rigorosas para governar o ciclo de vida de todo o conhecimento escrito da plataforma:

1. **Framework Diatáxis:** Toda documentação oficial deve ser alocada estritamente em um dos 4 quadrantes definidos pelo framework, correspondentes aos subdiretórios criados em `docs/`:
   - `1-tutorials/`: Para ensino e onboarding. Orientado ao aprendizado prático passo a passo.
   - `2-how-to/`: Receitas para resolver um problema pontual do dia a dia. Orientado a tarefas.
   - `3-reference/`: Especificações técnicas de schemas, classes e dados. Orientado a informações secas.
   - `4-explanation/`: Porquês arquiteturais, regras de negócios e ADRs. Orientado à compreensão sistêmica.
2. **Anotações Atômicas (Atomic Notes):** Cada documento no repositório não deve exceder um único escopo de conceito ou regra de negócio. Se um arquivo começar a cruzar múltiplos assuntos ou for maior que ~250 linhas, ele deve ser desmembrado.
   - *Regra semântica:* Um documento atômico deve ter **somente um cabeçalho H1 (`#`)**.

## 3. Consequências

**Positivas:**
- Reduz carga cognitiva: desenvolvedores com dúvidas práticas sabem que não precisam ler arquivos da pasta `4-explanation`.
- Promove a reutilização: anotações atômicas podem ser "linkadas" livremente entre si criando uma rede de conhecimento orgânica, semelhante a um sistema de *Zettelkasten*.
- Evita que guias rápidos fiquem defasados (fácil manutenção).

**Negativas / Trade-offs:**
- Um excesso de arquivos e divisões granulares. Desenvolvedores precisarão consultar os arquivos `index.md` / `README.md` regularmente para se localizarem ou usarem uma busca eficiente (`grep` / recursos da IDE).
- Curva de adaptação: requer disciplina no processo de review de Pull Requests para apontar e exigir correções nos locais em que documentações foram colocadas nos quadrantes errados.
