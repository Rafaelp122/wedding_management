# ADR-021: Padrão de Comentários e Docstrings

**Status:** Aceito
**Data:** Julho 2026
**Decisor:** Rafael
**Contexto:** Padronização da documentação no código e remoção de referências a ferramentas específicas.

---

## Contexto e Problema

O código-fonte possuía comentários dispersos com diferentes idiomas e estilos de documentação. Adicionalmente, havia comentários com referências explícitas a assistentes de codificação de IA (como "Bolt Optimization" e "Copilot Review Fix").

Isso trazia dois problemas:
1. **Poluição visual e acoplamento:** Referências a ferramentas externas poluem o histórico e a leitura do código de produção.
2. **Falta de consistência:** Métodos complexos sem parâmetros explicados aumentavam a carga cognitiva de onboarding.

---

## Decisão

1. Adotar formalmente o guia [COMMENTING_STANDARDS.md](../COMMENTING_STANDARDS.md) como a especificação única de escrita de documentação do Wedding Management System.
2. Adotar **Google Style** (em PT-BR) para docstrings de métodos de negócio (Services) e descrição curta para endpoints (API/Django Ninja).
3. Banir do código de produção qualquer menção a nomes de ferramentas de geração de código.

---

## Consequências

* **Positivas:**
  * Facilidade de onboarding e manutenção de longo prazo.
  * API Docs (Swagger) mais rica, pois o Django Ninja extrai automaticamente as docstrings dos endpoints para o OpenAPI.
  * Código limpo e independente de ferramentas ou ambientes.
