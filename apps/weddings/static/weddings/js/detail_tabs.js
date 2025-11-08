document.addEventListener('DOMContentLoaded', function() {
    const tabLinks = document.querySelectorAll('#abasCasamento .nav-link');
    const tabPanes = document.querySelectorAll('.tab-content .tab-pane');

    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Remove 'active' de todas as abas e esconde todos os painéis
            tabLinks.forEach(l => l.classList.remove('active'));
            tabPanes.forEach(pane => {
            pane.classList.remove('active');
            pane.classList.add('d-none');
            });

            // Adiciona 'active' à aba clicada e mostra o painel correspondente
            this.classList.add('active');
            const tabId = 'tab-' + this.dataset.tab;
            const content = document.getElementById(tabId);
            content.classList.remove('d-none');
            content.classList.add('active');
        });
    });

    // Dispara o clique (e o HTMX) na primeira aba ao carregar a página
    if (tabLinks.length > 0) {
        tabLinks[0].click();
    }
});
