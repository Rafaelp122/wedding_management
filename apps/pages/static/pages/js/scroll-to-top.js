// Botão Voltar ao Topo
(function() {
  'use strict';

  // Cria o botão dinamicamente
  const createScrollTopButton = () => {
    const button = document.createElement('button');
    button.id = 'scroll-to-top';
    button.className = 'scroll-to-top-btn';
    button.setAttribute('aria-label', 'Voltar ao topo');
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(button);
    return button;
  };

  // Inicializa o botão
  const scrollTopBtn = createScrollTopButton();

  // Mostra/esconde o botão baseado na posição do scroll
  const toggleButtonVisibility = () => {
    if (window.scrollY > 300) {
      scrollTopBtn.classList.add('visible');
    } else {
      scrollTopBtn.classList.remove('visible');
    }
  };

  // Scroll suave para o topo
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  // Event Listeners
  window.addEventListener('scroll', toggleButtonVisibility);
  scrollTopBtn.addEventListener('click', scrollToTop);

  // Verifica posição inicial
  toggleButtonVisibility();
})();
