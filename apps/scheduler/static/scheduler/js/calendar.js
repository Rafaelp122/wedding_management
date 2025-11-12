(function () {
  // Namespace global que mantém a instância ativa do calendário
  window.weddingApp = window.weddingApp || {};
  window.weddingApp.currentCalendar = null;

  // Inicializa o calendário quando o conteúdo HTMX da aba é carregado
  document.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target.id === "tab-scheduler") {
      if (window.weddingApp.currentCalendar) return;

      console.log("Inicializando calendário pela primeira vez...");

      // Aguarda a aba estar visível antes de renderizar
      setTimeout(function () {
        const calendarEl = document.getElementById("calendar");
        if (!calendarEl) {
          console.warn("Elemento #calendar não encontrado.");
          return;
        }

        const weddingId = calendarEl.dataset.weddingId;
        if (!weddingId) {
          console.error("ID do casamento não encontrado no calendário.");
          return;
        }

        const calendar = new FullCalendar.Calendar(calendarEl, {
          locale: "pt-br",
          height: 650,
          initialView: "dayGridMonth",
          headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
          },
          events: `/scheduler/api/events/?wedding_id=${weddingId}`,

          // Abre o modal de criação de evento
          dateClick: function (info) {
            const modalEl = document.getElementById("form-modal");
            if (!modalEl) return;
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            htmx.ajax("GET", `/scheduler/partial/${weddingId}/event/new/?date=${info.dateStr}`, {
              target: "#form-modal-container",
              swap: "innerHTML",
            });
            modal.show();
          },

          // Abre o modal de edição de evento existente
          eventClick: function (info) {
            const modalEl = document.getElementById("form-modal");
            if (!modalEl) return;
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            htmx.ajax("GET", `/scheduler/partial/${weddingId}/event/${info.event.id}/edit/`, {
              target: "#form-modal-container",
              swap: "innerHTML",
            });
            modal.show();
          },
        });

        calendar.render();
        window.weddingApp.currentCalendar = calendar;
        console.log("Calendário renderizado com sucesso.");
      }, 50);
    }
  });

  // Garante o redimensionamento correto ao reabrir a aba do calendário
  document.addEventListener("click", function (e) {
    const tabLink = e.target.closest('a[data-tab="scheduler"]');
    if (tabLink && window.weddingApp.currentCalendar) {
      setTimeout(function () {
        console.log("Atualizando layout do calendário (updateSize).");
        window.weddingApp.currentCalendar.updateSize();
      }, 50);
    }
  });
})();
