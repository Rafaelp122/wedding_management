(function () {
    /**
     * Inicializa o FullCalendar sempre que a aba "Calendário" for carregada via HTMX.
     */
    document.addEventListener("htmx:afterSwap", function (event) {
      // Verifica se o conteúdo injetado pertence à aba de calendário
      if (event.detail.target.id === "tab-scheduler") {
        console.log("HTMX carregou aba do calendário. Iniciando FullCalendar...");
  
        const calendarEl = document.getElementById("calendar");
        if (!calendarEl) {
          console.warn("Elemento #calendar não encontrado.");
          return;
        }
  
        // Obtém o ID do casamento a partir do atributo data
        const weddingId = calendarEl.dataset.weddingId;
        if (!weddingId) {
          console.error("ID do casamento não encontrado no elemento #calendar.");
          return;
        }
  
        // Remove qualquer instância anterior
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
          dateClick: function (info) {
            console.log("Data clicada:", info.dateStr);
            // Aqui depois podemos abrir modal HTMX para criar evento
          },
          eventClick: function (info) {
            console.log("Evento clicado:", info.event.title);
            // Aqui depois podemos abrir modal de edição
          },
        });
  
        // Guarda a instância para destruir depois se precisar
        calendarEl.fullCalendarInstance = calendar;
        calendar.render();
  
        console.log("FullCalendar renderizado com sucesso!");
      }
    });
  })();
  