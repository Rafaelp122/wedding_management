(function () {
  // Namespace global do calendário
  window.weddingApp = window.weddingApp || {};
  window.weddingApp.currentCalendar = null;

  // ===== Inicialização do calendário =====
  document.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target.id === "tab-scheduler") {
      if (window.weddingApp.currentCalendar) return;
      console.log("🟣 Inicializando calendário...");

      setTimeout(function () {
        const calendarEl = document.getElementById("calendar");
        if (!calendarEl) return console.warn("Elemento #calendar não encontrado.");

        const weddingId = calendarEl.dataset.weddingId;
        if (!weddingId) return console.error("ID do casamento não encontrado.");

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

          // Ações: novo evento / editar evento
          dateClick: function (info) {
            const modalEl = document.getElementById("form-modal");
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            htmx.ajax("GET", `/scheduler/partial/${weddingId}/event/new/?date=${info.dateStr}`, {
              target: "#form-modal-container",
              swap: "innerHTML",
            });
            modal.show();
          },
          eventClick: function (info) {
            const modalEl = document.getElementById("form-modal");
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
        console.log("✅ Calendário renderizado com sucesso.");
      }, 100);
    }
  });

  // ===== Ajuste visual ao trocar de aba =====
  document.addEventListener("click", function (e) {
    const tabLink = e.target.closest('a[data-tab="scheduler"]');
    if (tabLink && window.weddingApp.currentCalendar) {
      setTimeout(() => {
        console.log("↻ Atualizando tamanho do calendário...");
        window.weddingApp.currentCalendar.updateSize();
      }, 100);
    }
  });

  // ===== Eventos HTMX (criação, edição, exclusão) =====
  ["eventCreated", "eventUpdated", "eventDeleted"].forEach(eventName => {
    document.body.addEventListener(eventName, function (e) {
      console.log(`🔁 Trigger recebido: ${eventName}`, e.detail);
      if (window.weddingApp.currentCalendar) {
        window.weddingApp.currentCalendar.refetchEvents();
      }
      const modalEl = document.getElementById("form-modal");
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    });
  });

  // ===== Fechamento de modal via trigger adicional =====
  document.body.addEventListener("closeModal", function () {
    const modalEl = document.getElementById("form-modal");
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) {
      modal.hide();
      console.log("✅ Modal fechado automaticamente (closeModal).");
    }
  });
})();
