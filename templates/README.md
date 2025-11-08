# Documentação da Pasta de Templates

Esta pasta (`/templates`) contém os templates globais do projeto Django, responsáveis pela estrutura e layout base de todas as páginas.

## Estrutura de Herança

A organização dos templates segue um modelo de herança para maximizar a reutilização de código e manter a consistência visual. A hierarquia é a seguinte:

1.  `_base.html` (O esqueleto principal)
    - `base-public.html` (Layout para páginas públicas)
    - `base-auth.html` (Layout para páginas de autenticação)
    - `base-apps.html` (Layout para a área logada da aplicação)

Qualquer template de uma página específica (ex: `list.html`) deve herdar de um dos três layouts base (`public`, `auth`, ou `apps`).

---

## Templates Base

### `_base.html`

É o arquivo mais fundamental. Ele define a estrutura HTML principal (`<html>`, `<head>`, `<body>`), importa os arquivos CSS e JS globais e define os blocos (`{% block %}`) que os templates filhos irão preencher. **Não deve ser estendido diretamente por uma página.**

### `base-public.html`

Herda de `_base.html`. Define o layout para as páginas públicas do site (como a landing page). Geralmente inclui o `public-header.html` e o `footer.html`.

### `base-auth.html`

Herda de `_base.html`. Fornece a estrutura para as páginas de autenticação, como login, registro e recuperação de senha. O layout é tipicamente mais simples e focado na ação do formulário.

### `base-apps.html`

Herda de `_base.html`. É o layout principal para a área interna e logada da aplicação. Ele inclui o `apps-header.html`, a `sidebar.html` e a estrutura principal onde o conteúdo das páginas da aplicação é renderizado.

---

## Partials (`/partials`)

Esta pasta contém fragmentos de HTML reutilizáveis que são incluídos (`{% include %}`) nos templates base ou em outras páginas.

-   `_form_fields.html`: Um snippet para renderizar campos de formulário de maneira padronizada.
-   `apps-header.html`: O cabeçalho da área logada da aplicação.
-   `confirm_delete_modal.html`: Um modal genérico para confirmar ações de exclusão.
-   `footer.html`: O rodapé global do site.
-   `form.html`: Um template para renderizar um formulário completo, usando `_form_fields.html`.
-   `messages.html`: Responsável por exibir as mensagens de feedback do Django (ex: sucesso, erro, aviso).
-   `public-header.html`: O cabeçalho das páginas públicas.
-   `sidebar.html`: A barra de navegação lateral usada no `base-apps.html`.
