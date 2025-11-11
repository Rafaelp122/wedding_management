// Fecha modais globais após atualização de lista (padrão do sistema)
document.body.addEventListener('listUpdated', function() {
    closeAnyModal();
  });
  
  // Fecha modais após criar/editar um evento do calendário
  document.body.addEventListener('eventUpdated', function() {
    console.log('Evento salvo com sucesso. Atualizando calendário...');
    closeAnyModal();
  
    // Atualiza o calendário sem recarregar a página
    const calendarEl = document.getElementById('calendar');
    if (calendarEl && calendarEl.fullCalendarInstance) {
      calendarEl.fullCalendarInstance.refetchEvents();
    }
  });
  
  // Fecha modal explicitamente quando o backend dispara "closeModal"
  document.body.addEventListener('closeModal', function() {
    closeAnyModal();
  });
  
  
  // 🔹 Função genérica para fechar o modal aberto
  function closeAnyModal() {
    let modalEl = document.getElementById('form-modal');
    if (!modalEl) modalEl = document.getElementById('delete-modal');
  
    if (modalEl) {
      const modalInstance = bootstrap.Modal.getInstance(modalEl);
      if (modalInstance) modalInstance.hide();
      cleanupBackdrops();
    }
  }
  
  
  // 🔹 Helper para limpar fundos cinza e classes extras
  function cleanupBackdrops() {
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(b => b.remove());
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
  }
  