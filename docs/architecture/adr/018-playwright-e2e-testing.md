# ADR-018: Testes de Fim a Fim (E2E) com Playwright

## Status
Aceito

## Decisor
Rafael

## Contexto
À medida que o sistema de gerenciamento de casamentos cresce, a necessidade de garantir a integridade dos fluxos principais do usuário (como autenticação, fluxos financeiros e agendamentos) torna-se crítica. Testes unitários e de integração no frontend (Vitest + React Testing Library) e no backend (Pytest) não cobrem cenários onde múltiplos sistemas interagem no navegador real, incluindo injeções de estado local (como localStorage) e comportamento real de APIs.

Para mitigar regressões visuais e funcionais nos fluxos críticos, introduzimos uma infraestrutura de testes de Fim a Fim (E2E).

## Decisão
Adotamos o **Playwright** como a nossa ferramenta oficial de testes de Fim a Fim (E2E) para o frontend e fluxos críticos integrados.

### Detalhes da Decisão e Escolhas de Design:

1. **Escolha da Ferramenta (Playwright)**:
   - **Suporte Nativo a TypeScript**: Permite escrever testes robustos compartilhando tipos do frontend quando necessário, sem configurações adicionais.
   - **Velocidade de Execução**: Execução paralela extremamente rápida e isolamento nativo de contextos (BrowserContext).
   - **Experiência do Desenvolvedor (DX)**: Ferramentas como o Playwright Codegen, Inspector e Trace Viewer facilitam drasticamente a escrita e depuração de testes.
   - **Auto-waiting**: Reduz a fragilidade (flakiness) dos testes ao aguardar automaticamente que os elementos estejam acionáveis antes de interagir com eles.

2. **Estratégia de Sharding**:
   - Para manter o tempo de execução do pipeline curto no GitHub Actions (GHA), adotamos uma estratégia de sharding paralelo em 2 vias (`shard: 1/2` e `2/2`).

3. **Cobertura de Navegadores**:
   - Foco exclusivo no **Chromium** durante a execução de CI para otimizar o tempo de CI e economizar recursos computacionais, dado que a maior parte da nossa base de usuários e desenvolvedores utiliza motores baseados em Chromium e o comportamento de renderização moderna é altamente padronizado.

4. **Infraestrutura de Banco de Dados de Testes**:
   - Uso de banco de dados SQLite de desenvolvimento local que é populado sob demanda (on the fly) executando `python manage.py seed_db` antes do início dos testes. Isso garante dados previsíveis e consistentes para autenticação e outros fluxos de regressão sem depender de um banco de produção ou staging.

5. **Restrições de Execução em PRs**:
   - **Pull Requests (PR)**: Executamos apenas testes rápidos de fumaça (smoke tests) para validar que a aplicação inicia e a autenticação básica funciona sem quebrar o pipeline.
   - **Push na Branch Principal (`main`)**: Executamos o conjunto completo de testes de fumaça (smoke tests) e testes críticos de regressão para assegurar a estabilidade pré-deploy.

## Consequências
- **Positivas**:
  - Confiança significativamente maior nos deploys de frontend e integrações com o backend.
  - DX aprimorada com o uso de traces completos de falhas direto no CI.
  - Menor propensão a erros de autenticação e expiração de sessões no ambiente de produção.
- **Negativas**:
  - Custo adicional de tempo de execução no pipeline CI (mitigado pelo sharding e foco exclusivo em Chromium).
  - Necessidade de manter dados mockados/sementes de banco de dados atualizados no comando `seed_db`.
