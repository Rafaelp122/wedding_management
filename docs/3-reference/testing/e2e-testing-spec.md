# Especificação Técnica: Padrões de Teste E2E (`Playwright`)

> **Módulo:** [testing](index.md) | [ci-cd-pipeline-flow](../../4-explanation/architecture/ci-cd-pipeline-flow.md)
> **Camada:** Frontend E2E (`Playwright`)

---

## 1. Visão Geral

Os testes de fluxo ponta a ponta (E2E) com **Playwright** validam as jornadas críticas dos usuários da aplicação (Login, Navegação por Casamento, Criação de Fornecedor, Lançamento de Despesa e Notificações).

---

## 2. Estrutura de Pastas e Page Object Model (POM)

A suíte E2E fica localizada em `frontend/e2e/`:

```text
frontend/e2e/
├── fixtures.ts           # Fixtures de autenticação e setup de testes
├── pages/                # Page Object Models (POM)
│   ├── login.page.ts
│   └── weddings.page.ts
└── tests/
    ├── auth.spec.ts
    └── weddings.spec.ts
```

---

## 3. Padrões de Implementação

### 3.1 Prioridade de Locators
Ao interagir com a página, prefira locators resilientes e orientados a acessibilidade:

1. **Role-based (Recomendado)**:
   ```ts
   page.getByRole("button", { name: /salvar/i });
   page.getByRole("heading", { name: /casamentos/i });
   ```
2. **Label Text (Formulários)**:
   ```ts
   page.getByLabel(/nome do noivo/i);
   ```
3. **Test ID (Último Recurso)**:
   ```ts
   page.getByTestId("wedding-card");
   ```

### 3.2 Fixtures de Autenticação Reutilizáveis
Utilize fixtures estendidas para reutilizar sessões autenticadas e evitar refazer login em cada teste:

```ts
// frontend/e2e/fixtures.ts
export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill("planner@empresa.com");
    await page.getByLabel(/senha/i).fill("senha123");
    await page.getByRole("button", { name: /entrar/i }).click();
    await page.waitForURL("/dashboard");
    await use(page);
  },
});
```

---

## 4. Prevenção de Flaky Tests

1. **PROIBIDO `page.waitForTimeout(...)`**:
   NUNCA utilize pausas fixas por tempo (`waitForTimeout(3000)`).
2. **Aguarde Condições Reais**:
   Utilize `page.waitForURL()`, `page.waitForResponse()` ou asserções de visibilidade como `await expect(locator).toBeVisible()`.

---

## 5. Execução de Testes E2E

```bash
cd frontend && pnpm test:e2e
```
