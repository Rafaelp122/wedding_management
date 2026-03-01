# Camada de API — Guia de Uso

> Referência: [ADR-012](../ADR/012-orval-contract-driven-frontend.md)

Este projeto usa **Orval** para gerar automaticamente tipos TypeScript, hooks React Query e schemas Zod a partir do schema OpenAPI do backend. Esta página explica como funciona o fluxo e como consumir os artefatos gerados.

---

## Arquitetura

```
┌──────────────┐     make openapi     ┌───────────────┐     make orval     ┌──────────────────┐
│   Backend    │  ──────────────────► │ openapi.json  │ ──────────────────► │  generated/v1/   │
│ DRF + spec.  │                      │  (raiz)       │                     │ endpoints/models │
└──────────────┘                      └───────────────┘                     └──────────────────┘
```

| Comando | O que faz |
|---|---|
| `make openapi` | Gera `openapi.json` na raiz do projeto a partir do backend |
| `make orval` | Gera tipos, hooks e Zod schemas no frontend a partir do `openapi.json` |
| `make sync-api` | Executa ambos em sequência |

**Regra:** sempre rode `make sync-api` após alterar qualquer ViewSet, Serializer ou URL no backend.

---

## Estrutura de Arquivos

```
frontend/src/api/
├── axios-client.ts            ← Instância Axios com interceptors (editável)
├── custom-instance.ts         ← Mutator que o Orval injeta nos hooks (editável)
└── generated/                 ← ⚠️  NÃO EDITAR — sobrescrito a cada geração
    └── v1/
        ├── endpoints/         ← Hooks React Query agrupados por domínio
        │   ├── auth/
        │   ├── finances/
        │   ├── logistics/
        │   ├── scheduler/
        │   └── weddings/
        ├── models/            ← Interfaces TypeScript (request, response, enums, params)
        └── zod/               ← Schemas Zod para validação de formulários
```

### O que é editável vs gerado

| Arquivo | Editável? | Propósito |
|---|---|---|
| `axios-client.ts` | Sim | Configuração do Axios: baseURL, interceptors de auth, refresh token |
| `custom-instance.ts` | Sim | Adaptador entre o Orval e o Axios — o Orval injeta isso em cada hook |
| `generated/**` | **Não** | Qualquer edição será perdida no próximo `make sync-api` |

---

## Usando Hooks Gerados

### Leitura (queries)

Cada endpoint `GET` gera um hook `useXxx` que retorna dados tipados:

```tsx
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";

function WeddingList() {
  const { data, isLoading, error } = useWeddingsList();

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <ul>
      {data?.data.results.map((wedding) => (
        <li key={wedding.uuid}>{wedding.groom_name}</li>
      ))}
    </ul>
  );
}
```

O hook já encapsula a query key, a função de fetch e a tipagem. Não é necessário chamar Axios diretamente.

### Escrita (mutations)

Cada endpoint `POST`, `PUT`, `PATCH`, `DELETE` gera um hook `useXxxMutation`:

```tsx
import { useWeddingsCreate } from "@/api/generated/v1/endpoints/weddings/weddings";

function CreateWeddingForm() {
  const { mutate, isPending } = useWeddingsCreate();

  const onSubmit = (formData: WeddingRequest) => {
    mutate({ data: formData }, {
      onSuccess: () => { /* redirecionar, toastar, etc. */ },
    });
  };

  return <form onSubmit={handleSubmit(onSubmit)}>...</form>;
}
```

### Parâmetros de query (filtros, paginação)

Endpoints com query params ganham um tipo `XxxListParams`:

```tsx
import { useFinancesExpensesList } from "@/api/generated/v1/endpoints/finances/finances";

// Os parâmetros são tipados — autocompletar funciona
const { data } = useFinancesExpensesList({ wedding: weddingUuid, page: 2 });
```

---

## Usando Types Gerados

Os models ficam em `generated/v1/models/` e podem ser importados diretamente:

```tsx
import type { Wedding, WeddingRequest } from "@/api/generated/v1/models";
import type { WeddingStatusEnum } from "@/api/generated/v1/models";
```

Inclui:
- **Response types** (`Wedding`, `Budget`, `Expense`, etc.)
- **Request types** (`WeddingRequest`, `PatchedWeddingRequest`, etc.)
- **Enums** (`WeddingStatusEnum`, `ContractStatusEnum`, etc.)
- **Paginated wrappers** (`PaginatedWeddingList`, etc.)
- **Query params** (`WeddingsListParams`, `FinancesExpensesListParams`, etc.)

---

## Usando Schemas Zod

Os Zod schemas ficam em `generated/v1/zod/` e podem ser usados com `react-hook-form` + `@hookform/resolvers`:

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { weddingRequestSchema } from "@/api/generated/v1/zod/weddings/weddings";

const form = useForm({
  resolver: zodResolver(weddingRequestSchema),
});
```

Isso garante que a validação do formulário reflita as constraints do backend (required, maxLength, enum values, etc.) sem duplicar regras manualmente.

---

## Axios Client e Autenticação

O arquivo `axios-client.ts` configura:

1. **Base URL** — via `VITE_API_URL` ou fallback para `localhost:8000`.
2. **Interceptor de request** — injeta `Authorization: Bearer <token>` automaticamente.
3. **Interceptor de response** — tenta refresh do token em 401 e reenfileira requests pendentes.

Os hooks gerados pelo Orval usam essa instância via `custom-instance.ts`. Não é necessário passar headers ou tokens manualmente.

---

## Configuração do Orval

O arquivo `frontend/orval.config.ts` define dois targets:

| Target | Output | O que gera |
|---|---|---|
| `weddingApi` | `endpoints/` + `models/` | Hooks React Query + interfaces TypeScript |
| `weddingZod` | `zod/` | Schemas Zod para validação |

Opções relevantes:

- `mode: "tags-split"` — split por tag do OpenAPI (cada app Django = uma tag = um arquivo).
- `client: "react-query"` — gera hooks em vez de funções puras.
- `httpClient: "axios"` — usa Axios em vez de fetch nativo.
- `mutator` — aponta para `custom-instance.ts`, que é o ponto de extensão para auth, logging, etc.

---

## Fluxo de Trabalho Diário

```
1. Alterar Serializer/ViewSet/URL no backend
2. Rodar: make sync-api
3. Verificar os diffs em generated/ (novos tipos, campos, hooks)
4. Usar os hooks atualizados no frontend
5. Se o TypeScript reclamar → o contrato mudou → adaptar o frontend
```

Se o TypeScript **não** reclamar após uma mudança no backend, significa que o schema não foi regenerado. Rode `make sync-api` novamente.

---

## Troubleshooting

| Sintoma | Causa provável | Solução |
|---|---|---|
| Hook retorna `unknown` ou tipo genérico | Schema OpenAPI incompleto (serializer sem fields explícitos) | Verificar o serializer no backend e rodar `make sync-api` |
| Import não encontrado após novo endpoint | `make sync-api` não foi rodado | Rodar `make sync-api` |
| Tipo gerado não reflete campo adicionado | Cache do Orval ou `openapi.json` desatualizado | Rodar `make sync-api` (regenera tudo) |
| Erro de runtime mas tipo está correto | `openapi.json` divergiu da implementação real | Verificar se o backend está rodando e rodar `make sync-api` |
