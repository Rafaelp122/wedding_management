document.body.addEventListener('click', function(e) {
    
    // Procura pelo 'card-wrapper' clicável
    const cardWrapper = e.target.closest('.card-wrapper');

    // Ignora se não for um card-wrapper ou se o clique foi num link, botão ou form
    if (!cardWrapper || e.target.closest('a') || e.target.closest('button') || e.target.closest('form')) {
      return;
    }

    // Redireciona para a página de detalhes
    const link = cardWrapper.getAttribute('data-href');
    if (link) {
      window.location.href = link;
    }
});
