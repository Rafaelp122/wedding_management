# Especificação Técnica: Workflows de IA (`ai-code-review.yml` & `opencode-assistant.yml`)

> **Módulo:** [ci-cd](index.md) | [ci-cd-pipeline-flow](../../4-explanation/architecture/ci-cd-pipeline-flow.md)
> **Workflows:** `.github/workflows/ai-code-review.yml` | `.github/workflows/opencode-assistant.yml`

---

## 1. Visão Geral

Os workflows de IA realizam auditorias automáticas de código e prestam assistência interativa aos desenvolvedores diretamente nos Pull Requests do GitHub.

---

## 2. Workflows Implementados

### 2.1 `ai-code-review.yml` (Revisão Automática por SHA)
- **Gatilho**: Disparado automaticamente na abertura ou atualização de Pull Requests.
- **Isolamento de Estado**: Analisa estritamente o diff do SHA atual do commit. Não utiliza labels do GitHub como armazenamento de estado.
- **Auditoria de Qualidade**: Avalia o diff procurando violações de multi-tenancy, queries N+1, falhas de acessibilidade e quebras do padrão da camada de serviços (`services.py`).
- **Feedback**: Publica o relatório da revisão como comentário estruturado no PR.

### 2.2 `opencode-assistant.yml` (Assistente Interativo)
- **Gatilho**: Disparado sob demanda quando um desenvolvedor comenta `@opencode` em um Pull Request ou issue.
- **Capacidade**: Executa diagnósticos de falhas de teste, gera sugestões de refatoração e auxilia na resolução de dúvidas de arquitetura.
