/* ====== Event Modal Controller (Integration with FullCalendar) ====== */

(function() {
  console.log("LOG MODAL v2: Script do _event_form_modal_content.html iniciado.");

  /* Referências principais */
  const form = document.getElementById('event-modal-form');
  const deleteButton = document.getElementById('delete-event-button');
  const csrfTokenInput = form?.querySelector('[name=csrfmiddlewaretoken]');

  /* Validação inicial */
  if (!form) {
    console.error("ERRO MODAL v2: Formulário #event-modal-form não encontrado.");
    return;
  }
  if (!csrfTokenInput) {
    console.warn("LOG MODAL v2: Campo CSRF token ausente — operação pode ser limitada.");
  }

  /* Listener de envio do formulário */
  form.removeEventListener('submit', handleFormSubmit);
  form.addEventListener('submit', handleFormSubmit);
  console.log("LOG MODAL v2: Listener de 'submit' aplicado.");

  /* Listener do botão de exclusão */
  if (deleteButton) {
    deleteButton.removeEventListener('click', handleDeleteClick);
    deleteButton.addEventListener('click', handleDeleteClick);
    console.log("LOG MODAL v2: Listener de 'click' aplicado ao botão excluir.");
  } else {
    console.log("LOG MODAL v2: Botão de exclusão não encontrado (modo criação).");
  }

  /* ===== Submissão do formulário ===== */
  function handleFormSubmit(e) {
    e.preventDefault();
    console.log("LOG MODAL v2: Submissão interceptada.");

    const formData = new FormData(form);
    const dataToSend = {
      action: 'modal_save',
      event_id: formData.get('event_id') || null,
      form_data: {}
    };

    /* Serializa os campos do formulário */
    for (const [key, value] of formData.entries()) {
      if (!['csrfmiddlewaretoken', 'action', 'event_id'].includes(key)) {
        dataToSend.form_data[key] = value;
      }
    }

    /* Envia via função global do calendário */
    if (typeof sendCalendarUpdate === 'function') {
      console.log("LOG MODAL v2: Enviando dados para sendCalendarUpdate...");
      sendCalendarUpdate(dataToSend);
    } else {
      console.error("ERRO MODAL v2: Função 'sendCalendarUpdate' não encontrada.");
      alert("Erro: Não foi possível enviar os dados. O evento não foi salvo.");
    }
  }

  /* ===== Exclusão de evento ===== */
  function handleDeleteClick(e) {
    e.preventDefault();
    console.log("LOG MODAL v2: Clique no botão de exclusão.");

    if (!confirm('Tem certeza que deseja excluir este evento?')) {
      console.log("LOG MODAL v2: Exclusão cancelada pelo usuário.");
      return;
    }

    const eventIdInput = form.querySelector('[name=event_id]');
    if (!eventIdInput || !eventIdInput.value) {
      console.error("ERRO MODAL v2: ID do evento não encontrado.");
      alert("Erro: Não foi possível identificar o evento para exclusão.");
      return;
    }

    const dataToSend = {
      action: 'delete',
      event_id: eventIdInput.value
    };

    /* Executa exclusão via função global */
    if (typeof sendCalendarUpdate === 'function') {
      console.log("LOG MODAL v2: Enviando requisição de exclusão...");
      sendCalendarUpdate(dataToSend);
    } else {
      console.error("ERRO MODAL v2: Função 'sendCalendarUpdate' não encontrada.");
      alert("Erro: Não foi possível contactar o servidor. O evento não foi excluído.");
    }
  }

})();
