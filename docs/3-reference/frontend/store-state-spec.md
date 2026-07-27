# Especificação Técnica: Gerenciamento de Estado (Zustand Stores & TanStack Query)

> **Módulo:** [frontend-reference](index.md) | [system-overview](../../4-explanation/architecture/system-overview.md)
> **Camada:** Frontend (`src/stores/`, `src/api/generated/`, `src/features/weddings/hooks/`)

---

## Visão Geral

A aplicação adota uma estratégia clara de separação de estados:
1. **Estado de Servidor (Server State):** Gerenciado exclusivamente por **TanStack Query** através dos hooks gerados pelo **Orval** (`src/api/generated/`).
2. **Estado Global da Aplicação (Client State):** Gerenciado por **Zustand** para dados globais persistentemente necessários no cliente (Sessão, Tenant Selecionado, Casamento Ativo).

---

## Zustand Stores Globais

### `useAuthStore` (`src/stores/authStore.ts`)
- **Responsabilidade:** Armazena o estado de autenticação do usuário e tokens JWT.
- **Propriedades:** `user`, `accessToken`, `refreshToken`.
- **Ações:** `setAuth(user, accessToken, refreshToken)`, `clearAuth()`.

### `useWeddingStore` (`src/stores/weddingStore.ts`)
- **Responsabilidade:** Armazena o casamento selecionado no contexto atual da assessoria.
- **Propriedades:** `activeWedding: Wedding | null`.
- **Ações:** `setActiveWedding(wedding: Wedding | null)`.

---

## Padrões Avançados de Performance & UX

### 1. Renderização Instantânea via `placeholderData` Cache Lookup (`useWeddingDetail`)
Para evitar spinners de carregamento ao clicar em um casamento na lista, o hook `useWeddingDetail(uuid)` inspeciona previamente o cache das queries de lista (`/api/v1/weddings/`) no TanStack Query:

```typescript
const queryResult = useWeddingsRead(uuid, {
  query: {
    enabled: !!uuid,
    placeholderData: () => {
      const cachedQueries = queryClient.getQueriesData<AxiosResponse<PagedWeddingOut>>({
        queryKey: ["/api/v1/weddings/"],
      });
      for (const [, queryData] of cachedQueries) {
        const weddingItem = queryData?.data?.items?.find((item) => item.uuid === uuid);
        if (weddingItem) return { data: weddingItem, status: 200, ... };
      }
      return undefined;
    },
  },
});
```
*Resultado:* O cabeçalho e dados básicos do casamento são exibidos **instantaneamente** na tela enquanto a consulta completa é sincronizada em segundo plano.

---

### 2. Isolation de Bundle via Lazy Loading de Abas (`WeddingDetailTabs.tsx`)
A página de detalhes do casamento orquestra visões complexas de outros domínios (Finanças, Fornecedores e Cronograma). Para otimizar a carga inicial da página, as visões das abas são carregadas dinamicamente via `React.lazy()` e encapsuladas por `<Suspense fallback={<TabLoadingSkeleton />}>`:

- `FinancesView` (`@/features/finances`)
- `VendorsItemsView` (`@/features/logistics`)
- `SchedulerPage` (`@/features/scheduler`)

---

## Invalidação de Cache com Orval Keys

Sempre invalide as chaves geradas pelo Orval no `onSuccess` ou via seletores centralizados (`invalidateWeddingQueries`):

```ts
const queryClient = useQueryClient();
queryClient.invalidateQueries({ queryKey: getWeddingsReadQueryKey(uuid) });
queryClient.invalidateQueries({ queryKey: getWeddingsListQueryKey() });
```
