## 📝 Resumo do Pull Request

<!-- DICA: Se você deixar esta seção em branco, o gerador de IA ("AI PR Description") preencherá automaticamente com o resumo do diff no formato abaixo ao abrir a PR. -->

### O que muda
-

### Por quê
-

### Como testar
-

---

## 🛠️ Checklist do Desenvolvedor (Quality Gates)

Antes de abrir a PR ou marcar como pronta para revisão, certifique-se de que cumpriu os seguintes requisitos:

- [ ] **Lint & Format:** Executei `make lint` localmente e o código está formatado (Ruff/ESLint).
- [ ] **Testes locais:** Executei `make test` e todos os testes passaram com sucesso.
- [ ] **Migrações:** Se houver alterações em modelos do Django, verifiquei com `make migrate-check` (evitando falhas de makemigrations no CI).
- [ ] **Segurança (Secrets):** Verifiquei que nenhuma credencial, chave de API ou segredo estático foi exposto no código.
- [ ] **Arquitetura (Backend):** Toda a lógica de negócio está em `services.py` (e não em `api.py`) e as queries filtram por tenant usando `for_tenant(company)`.
- [ ] **Arquitetura (Frontend):** Não utilizei `fetch` ou `axios` manualmente; consumi a API exclusivamente pelos hooks gerados pelo Orval.

---

## 🤖 Interagindo com o OpenCode AI Assistant

Este repositório está integrado com o **OpenCode Assistant** para automatizar tarefas. Você pode interagir com o agente diretamente nos comentários desta PR utilizando o comando `/oc`.

> [!IMPORTANT]
> Apenas **Owners**, **Members** e **Collaborators** do repositório têm autorização para disparar o assistente. Comentários de usuários externos serão ignorados por segurança.

### Comandos Úteis que você pode usar:

* **Aplicar Correções Automáticas:**
  Se a revisão automática (ou um revisor humano) apontar um problema em uma linha de código, basta responder na mesma thread do comentário com:
  > `/oc corrija isso` ou `/oc corrija usando docker compose rm`
  *(O assistente fará o checkout da branch, aplicará a correção, rodará os testes e subirá o commit automaticamente).*

* **Escrever Testes Automatizados:**
  Peça para o assistente gerar a suíte de testes de um arquivo recém-criado:
  > `/oc crie os testes unitários da função X em apps/weddings/services.py`

* **Validar contra Diretrizes do Projeto:**
  Peça para ele checar se o código atende às especificações gerais:
  > `/oc valide as alterações do backend contra as regras do AGENTS.md`

* **Explicar trechos de código:**
  > `/oc explique o funcionamento do fluxo de autenticação WIF no integrity-ci.yml`
