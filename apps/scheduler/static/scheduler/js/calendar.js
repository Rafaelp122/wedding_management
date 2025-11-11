// =============================================================
// FULLCALENDAR + HTMX - Integração completa e reativa
// =============================================================
(function () {
    document.addEventListener("htmx:afterSwap", function (event) {
      // Só roda quando a aba do calendário for carregada
      if (event.detail.target.id === "tab-scheduler") {
        console.log("✅ HTMX carregou aba do calendário. Iniciando FullCalendar...");
  
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
  
        // Se já existir um calendário ativo, destrói antes de recriar
        if (calendarEl.fullCalendarInstance) {
          calendarEl.fullCalendarInstance.destroy();
        }
  
        // Inicializa o FullCalendar
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
  
          // Clique em uma data → abre modal HTMX de criação
          dateClick: function (info) {
            console.log("📅 Data clicada:", info.dateStr);
            const modal = new bootstrap.Modal(document.getElementById("form-modal"));
  
            htmx.ajax("GET", `/scheduler/partial/${weddingId}/event/new/?date=${info.dateStr}`, {
              target: "#form-modal-container",
              swap: "innerHTML"
            });
  
            modal.show();
          },
  
          // Clique em um evento → (depois) abrir modal de edição
          eventClick: function (info) {
            console.log("🟣 Evento clicado:", info.event.title);
            const modal = new bootstrap.Modal(document.getElementById("form-modal"));
  
            htmx.ajax("GET", `/scheduler/partial/${weddingId}/event/${info.event.id}/edit/`, {
              target: "#form-modal-container",
              swap: "innerHTML"
            });
  
            modal.show();
          }
        });
  
        calendar.render();
  
        // Guarda referência global para uso no modal_handler.js
        calendarEl.fullCalendarInstance = calendar;
  
        console.log("✅ FullCalendar renderizado e pronto!");
      }
    });
  })();
  