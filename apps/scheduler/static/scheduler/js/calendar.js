(function () {
  window.weddingApp = window.weddingApp || {};
  window.weddingApp.currentCalendar = null;

  // Cor fixa por evento
  function getEventColor(eventId) {
    const key = `event_color_${eventId}`;
    let color = localStorage.getItem(key);

    if (!color) {
      color = `hsl(${Math.floor(Math.random() * 360)}, 70%, 80%)`;
      localStorage.setItem(key, color);
    }

    return color;
  }

  // Inicializa calendário quando aba scheduler carregar
  document.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target.id !== "tab-scheduler") return;
    if (window.weddingApp.currentCalendar) return;

    setTimeout(function () {
      const calendarEl = document.getElementById("calendar");
      if (!calendarEl) return;

      const weddingId = calendarEl.dataset.weddingId;

      const calendar = new FullCalendar.Calendar(calendarEl, {
        locale: "pt-br",
        height: "auto",
        expandRows: true,
        initialView: "dayGridMonth",
        displayEventTime: false,   

        headerToolbar: {
          left: "prev,next today",
          center: "title",
          right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
        },

        events: `/scheduler/api/events/?wedding_id=${weddingId}`,

        // Tooltip + cor fixa
        eventDidMount: function (info) {
          const color = getEventColor(info.event.id);
          info.el.style.backgroundColor = color;
          info.el.style.borderColor = color;

          let tooltip = `Título: ${info.event.title || "—"}`;

          if (info.event.extendedProps.type)
            tooltip += `\nTipo: ${info.event.extendedProps.type}`;

          if (info.event.extendedProps.location)
            tooltip += `\nLocal: ${info.event.extendedProps.location}`;

          if (info.event.start) {
            const inicio = info.event.start.toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit",
            });
            tooltip += `\nInício: ${inicio}`;
          }

          if (info.event.end) {
            const fim = info.event.end.toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit",
            });
            tooltip += `\nFim: ${fim}`;
          }

          if (info.event.extendedProps.description)
            tooltip += `\nDescrição: ${info.event.extendedProps.description}`;

          info.el.setAttribute("title", tooltip);
        },

        // Criar evento
        dateClick: function (info) {
          const modalEl = document.getElementById("form-modal");
          const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

          htmx.ajax(
            "GET",
            `/scheduler/partial/${weddingId}/event/new/?date=${info.dateStr}`,
            { target: "#form-modal-container", swap: "innerHTML" }
          );

          modal.show();
        },

        // Editar evento
        eventClick: function (info) {
          const modalEl = document.getElementById("form-modal");
          const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

          htmx.ajax(
            "GET",
            `/scheduler/partial/${weddingId}/event/${info.event.id}/edit/`,
            { target: "#form-modal-container", swap: "innerHTML" }
          );

          modal.show();
        }
      });

      calendar.render();
      window.weddingApp.currentCalendar = calendar;

    }, 100);
  });

  // Atualiza tamanho ao trocar aba
  document.addEventListener("click", function (e) {
    const tab = e.target.closest('a[data-tab="scheduler"]');
    if (!tab || !window.weddingApp.currentCalendar) return;

    setTimeout(() => {
      window.weddingApp.currentCalendar.updateSize();
    }, 100);
  });

  // Atualiza após create/edit/delete
  ["eventCreated", "eventUpdated", "eventDeleted"].forEach(evt => {
    document.body.addEventListener(evt, function () {
      if (window.weddingApp.currentCalendar)
        window.weddingApp.currentCalendar.refetchEvents();

      const modalEl = document.getElementById("form-modal");
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    });
  });

  // Fechar modal via evento customizado
  document.body.addEventListener("closeModal", function () {
    const modalEl = document.getElementById("form-modal");
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
  });

})();
