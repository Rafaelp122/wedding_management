# App: Weddings

O app `weddings` é o núcleo da aplicação, responsável por gerenciar a entidade principal do sistema: o Casamento (`Wedding`). Ele lida com a criação, visualização, listagem e todos os detalhes associados a um casamento.

---

## Responsabilidades

-   **Gerenciamento de Casamentos:** Define o modelo `Wedding` e fornece as interfaces para que os usuários possam criar e gerenciar seus casamentos.
-   **Visualização de Detalhes:** Apresenta uma página de detalhes completa para cada casamento, que serve como um painel central para acessar outras funcionalidades relacionadas (Orçamento, Contratos, etc.).
-   **Listagem de Eventos:** Exibe todos os casamentos associados a um usuário.

---

## Estrutura de Arquivos

### Arquivos Python

-   `models.py`: Define o `Wedding`, modelo de dados central que armazena informações como nome dos noivos, data e local.
-   `views.py`: Contém a lógica para renderizar as páginas, utilizando Class-Based Views (CBVs) e Mixins para máxima reutilização de código.

    -   **Mixins:**
        -   `WeddingBaseMixin`: Centraliza a lógica de negócio principal. É responsável por:
            - Filtrar casamentos por usuário (`planner`).
            - Anotar a queryset com contagens de itens e contratos.
            - Gerar a resposta HTMX que atualiza a lista de casamentos na tela após uma criação, edição ou exclusão.
        -   `WeddingFormLayoutMixin`: Padroniza a renderização dos formulários de criação e edição. Define o `form_class`, o template do formulário (`_create_wedding_form.html`) e injeta no contexto os dados de layout (classes CSS e ícones para os campos).

    -   **Views:**
        -   `WeddingListView`: Exibe a lista de casamentos do usuário, utilizando o `WeddingBaseMixin` para obter os dados.
        -   `WeddingCreateView`: Manipula a criação de um novo casamento. Usa o `WeddingFormLayoutMixin` para o formulário e o `WeddingBaseMixin` para processar a resposta HTMX.
        -   `WeddingUpdateView`: Permite a edição de um casamento existente, reutilizando a mesma lógica de formulário e resposta HTMX dos mixins.
        -   `WeddingDeleteView`: Gerencia a exclusão de um casamento. Apresenta um modal de confirmação e, após a exclusão, atualiza a lista via HTMX com a ajuda do `WeddingBaseMixin`.
        -   `WeddingDetailView`: Exibe a página de detalhes de um casamento específico. É a única view que não utiliza os mixins principais, pois sua função é apenas exibir um objeto.
        
-   `urls.py`: Mapeia as URLs (ex: `/weddings/`, `/weddings/<id>/`) para as views correspondentes.
-   `forms.py`: Contém o `WeddingForm`, formulário usado para criar e editar casamentos.
-   `admin.py`: Registra o modelo `Wedding` para que ele possa ser gerenciado através da interface de administração do Django.

### Templates (`templates/weddings/`)

-   `list.html`: A página principal que exibe a lista de "Meus Casamentos".
-   `detail.html`: O painel de detalhes de um casamento específico, que contém as abas para outras funcionalidades (Orçamento, Contratos, Itens, Calendário).
-   **`partials/`**: Contém fragmentos de template reutilizáveis.
    -   `_wedding_list_content.html`: Renderiza a lista de cards de casamento.
    -   `_wedding_card.html`: O template para um único card de casamento na lista.
    -   `_create_wedding_form.html`: O formulário de criação de casamento, projetado para ser carregado via HTMX em um modal.

### Arquivos Estáticos (`static/weddings/`)

Assets específicos para o app `weddings`.

-   **`css/`**:
    -   `list.css`: Estilos para a página de listagem de casamentos.
    -   `detail.css`: Estilos para a página de detalhes do casamento.
-   **`js/`**:
    -   `clickable_cards.js`: Adiciona a funcionalidade que torna os cards na lista de casamentos clicáveis.
    -   `detail_tabs.js`: Gerencia o comportamento de navegação por abas na página de detalhes.
