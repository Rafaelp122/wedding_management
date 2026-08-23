# ADR-012: Geração Automática da Camada de API do Frontend via Orval

**Status:** Aceito
**Data:** Março 2026
**Decisor:** Rafael
**Contexto:** Eliminar código manual de clients HTTP, tipos TypeScript e hooks React Query no frontend

---

## Contexto e Problema

O frontend precisa se comunicar com a API REST do backend. Sem automação, cada endpoint exige:

1. **Tipo TypeScript** — interface de request e response, enums, paginação.
2. **Função de fetch** — chamada Axios com URL, método, headers, parâmetros.
3. **Hook React Query** — `useQuery` para leitura, `useMutation` para escrita, query keys, invalidação.
4. **Schema de validação** — Zod schema para validar formulários no frontend.

Manter isso manualmente cria 4 problemas:

| Problema | Consequência |
|---|---|
| **Drift silencioso** | Backend muda um campo e o frontend não percebe até runtime |
| **Boilerplate massivo** | Cada endpoint gera ~50-100 linhas de código manual repetitivo |
| **Erros de digitação** | Typos em nomes de campos, URLs, enums passam pelo TypeScript se os tipos forem manuais |
| **Custo de onboarding** | Novo dev precisa entender a convenção de hooks, query keys, etc. |

O backend já expõe um schema OpenAPI completo via `drf-spectacular`, o que viabiliza a geração automática.

---

## Decisão

Usar **Orval** como gerador de código, configurado com:

- **Client:** `react-query` — gera hooks `useQuery` e `useMutation` do TanStack React Query.
- **HTTP Client:** `axios` — usa uma instância Axios customizada com interceptors de auth e refresh token.
- **Schemas:** TypeScript interfaces geradas a partir dos schemas OpenAPI.
- **Validação:** Zod schemas gerados em target separado para uso em formulários.
- **Splitting:** `tags-split` — um arquivo por tag/domínio (weddings, finances, logistics, scheduler, auth).
- **Mutator:** Instância Axios customizada (`custom-instance.ts`) para centralizar autenticação e error handling.

### Pipeline de sincronização

```
Backend (Django + DRF + drf-spectacular)
  │
  ▼  make openapi
openapi.json (raiz do projeto — versionado)
  │
  ▼  make orval
frontend/src/api/generated/ (código gerado — versionado)
```

O comando `make sync-api` executa ambos os passos em sequência.

---

## Estrutura Gerada

```
frontend/src/api/
├── axios-client.ts              # Instância Axios + interceptors (MANUAL)
├── custom-instance.ts           # Mutator do Orval — adapta Axios (MANUAL)
└── generated/                   # ⚠️ NUNCA EDITAR — sobrescrito pelo Orval
    └── v1/
        ├── endpoints/           # Hooks React Query (useQuery, useMutation)
        │   ├── auth/
        │   ├── finances/
        │   ├── logistics/
        │   ├── scheduler/
        │   └── weddings/
        ├── models/              # Interfaces TypeScript (request, response, enums)
        │   ├── wedding.ts
        │   ├── weddingRequest.ts
        │   ├── budget.ts
        │   └── ...
        └── zod/                 # Zod schemas para validação de formulários
            ├── finances/
            ├── logistics/
            └── ...
```

---

## Alternativas Consideradas

### 1. Código manual de hooks e tipos

**Rejeitado.** Boilerplate massivo, drift silencioso, alto custo de manutenção. Era viável com 2-3 endpoints, mas o projeto tem 30+.

### 2. `openapi-typescript` + `openapi-fetch`

Gera apenas tipos TypeScript e um client fetch leve sem framework de estado. **Rejeitado** porque:
- Não gera hooks React Query — teríamos que escrevê-los manualmente.
- Não gera Zod schemas.
- Menos ecossistema para customização (mutators, transformers).

### 3. `swagger-typescript-api`

Gera client completo com tipos. **Rejeitado** porque:
- Gera classes (OOP) em vez de funções + hooks — estilo incompatível com React funcional.
- Não tem integração nativa com React Query.
- Não gera Zod schemas.

### 4. GraphQL (Apollo / urql)

Eliminaria o problema com codegen nativo. **Rejeitado** porque:
- Reescrita completa do backend (DRF → Graphene/Strawberry).
- Overhead desproporcional para o tamanho do projeto.
- REST + OpenAPI já resolve o contrato tipado com Orval.

---

## Consequências

### Positivas

- **Zero drift:** Tipos do frontend são derivados diretamente do schema do backend. Se um campo mudar, o TypeScript quebra no build — não em produção.
- **Zero boilerplate de fetch:** Hooks prontos com query keys, enabled, onSuccess, etc.
- **Validação sincronizada:** Zod schemas gerados garantem que a validação do formulário reflete as constraints do backend.
- **Onboarding simplificado:** Novo dev importa um hook e usa. Não precisa saber a URL, método ou formato.

### Negativas

- **Dependência do Orval:** Se o projeto for descontinuado, precisamos migrar. Mitigação: o código gerado é vanilla TypeScript + React Query — legível e editável se necessário.
- **Schema OpenAPI como gargalo:** Se o `drf-spectacular` gerar um schema incorreto, o frontend herda o erro. Mitigação: o schema é versionado e revisável em PR.
- **Diretório `generated/` versionado:** Aumenta o diff em PRs que mudam a API. Mitigação: colapsar a pasta em code review; a alternativa (gerar no CI) impede type-checking local.

---

## Referências

- [Orval docs](https://orval.dev)
- [TanStack React Query](https://tanstack.com/query)
- [drf-spectacular](https://drf-spectacular.readthedocs.io)
- ADR-006: Service Layer Pattern (define os endpoints que geram o schema)
