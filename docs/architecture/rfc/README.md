# Requests for Comments (RFCs)

> **Módulo:** [Arquitetura & Engenharia](../index.md) · [Índice de ADRs (001–031)](../adr/README.md) · [Topologia de Domínios](../domains/index.md)
> **Escopo:** Catálogo Oficial de Propostas de Macro-Arquitetura, System Design e Escopo

---

## 1. Visão Geral

As **Requests for Comments (RFCs)** representam o instrumento formal de proposição, deliberação e registro de grandes decisões arquiteturais, redesenho de domínios e consolidação de escopo no **Wedding Management System**.

Diferente das **ADRs (Architecture Decision Records)** — que capturam decisões atômicas, pontuais e imutáveis (como a escolha de uma biblioteca, banco de dados ou tecnologia específica) —, uma **RFC** atua como uma proposta técnica abrangente (*Technical Design Document*), amarrando múltiplos Bounded Contexts, fluxos de ponta a ponta e a estratégia evolutiva do produto.

---

## 2. Legenda do Ciclo de Vida das RFCs

| Status | Significado Arquitetural |
| :--- | :--- |
| 🟡 **Proposta** | Documento em fase inicial de elaboração e levantamento de requisitos. |
| 🔵 **Em Revisão** | Documento aberto para discussão técnica, revisão de pares e análise de trade-offs. |
| 🟢 **Aprovada** | Proposta homologada e acordada como a direção oficial da arquitetura. |
| 🟣 **Implementada** | Mudanças técnicas, migrações de banco e refatorações concluídas em produção. |
| ⚪ **Substituída** | RFC histórica cujo conteúdo foi superado por uma nova proposta arquitetural. |

---

## 3. Catálogo de Propostas Arquiteturais (RFCs)

| Identificador | Título da Proposta | Status | Data de Aprovação | Bounded Contexts Impactados |
| :--- | :--- | :--- | :--- | :--- |
| **[RFC-001](001-macro-architecture-and-domain-redesign.md)** | **Macro-Arquitetura da Plataforma SaaS, Escopo Consolidado e Redesenho de Domínios** | 🟢 Aprovada | Setembro 2026 | `weddings`, `contracts`, `finances`, `logistics`, `scheduler`, `dashboard`, `reporting`, `notifications` |

---

## 4. Estrutura Padrão de uma RFC

Toda nova RFC submetida ao projeto deve seguir a estrutura canônica:

1. **Resumo Executivo (Summary):** Explicação concisa da proposta e seus objetivos.
2. **Contexto & Motivação (Motivation):** O problema que está sendo resolvido e os limites da arquitetura atual.
3. **Fluxo Operacional de Ponta a Ponta (User Journey):** A jornada do usuário e dos dados através das fases do negócio.
4. **Design de Domínios & Entidades:** Detalhamento dos Bounded Contexts, raízes de agregação e modelos.
5. **Comunicação Inter-Módulos:** Matriz híbrida de interfaces síncronas e eventos de domínio assíncronos.
6. **Estratégia de Implementação & Migração:** Fases de transição de dados e compatibilidade com código existente.
