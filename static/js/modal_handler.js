// Script para fechar qualquer modal após uma atualização de lista
document.body.addEventListener('listUpdated', function(evt) {
    
    // Tenta encontrar o modal de formulário
    let modalEl = document.getElementById('form-modal');
    
    // Se não encontrou (for nulo), tenta encontrar o modal de deleção
    if (!modalEl) {
        modalEl = document.getElementById('delete-modal');
    }

    // Se encontrou qualquer um dos dois...
    if (modalEl) {
        const modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (modalInstance) {
            modalInstance.hide(); 
        }
        
        // Limpa o fundo cinza
        cleanupBackdrops();
    }
});

// Helper para não repetir o código de limpeza
function cleanupBackdrops() {
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(b => b.remove());
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
}
