// Script para fechar o modal
document.body.addEventListener('weddingCreated', function(evt) {
  const modalEl = document.getElementById('main-modal');
  if (modalEl) {
    const modalInstance = bootstrap.Modal.getInstance(modalEl);
    if (modalInstance) {
      modalInstance.hide(); 
    }
    
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(b => b.remove());

    document.body.classList.remove('modal-open');
    document.body.style.overflow = ''; // Garante que o scroll da página volte
  }
});
