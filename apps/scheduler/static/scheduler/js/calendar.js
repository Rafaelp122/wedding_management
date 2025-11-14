(function () {
  window.weddingApp = window.weddingApp || {};
  window.weddingApp.currentCalendar = null;

  // Retorna uma cor fixa por evento (persistente via localStorage)
  function getEventColor(eventId) {
    const key = `event_color_${eventId}`;
    let color = localStorage.getItem(key);

    if (!color) {
      color = `hsl(${Math.floor(Math.random() * 360)}, 70%, 80%)`;
      localStorage.setItem(key, color);
    }
    return color;
  }

  // Inicializa o calendário quando a aba "scheduler" é carregada
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

        headerToolbar: {
          left: "prev,next today",
          center: "title",
          right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
        },

        events: `/scheduler/api/events/?wedding_id=${weddingId}`,

        // Aplica cor fixa e tooltip aos eventos
        eventDidMount: function (info) {
          const color = getEventColor(info.event.id);

          info.el.style.backgroundColor = color;
          info.el.style.borderColor = color;

          let tooltip = info.event.title || "";

          if (info.event.extendedProps.description) {
            tooltip += "\n" + info.event.extendedProps.description;
          }

          if (info.event.start) {
            const time = info.event.start.toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit"
            });
            tooltip += "\n" + time;
          }

          info.el.setAttribute("title", tooltip);
        },

        // Ação: Criar novo evento ao clicar em uma data
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

        // Ação: Editar evento ao clicar no bloquinho
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

  // Ajusta o tamanho do calendário ao alternar abas
  document.addEventListener("click", function (e) {
    const tabLink = e.target.closest('a[data-tab="scheduler"]');
    if (!tabLink || !window.weddingApp.currentCalendar) return;

    setTimeout(() => {
      window.weddingApp.currentCalendar.updateSize();
    }, 100);
  });

  // Recarrega eventos após criar/editar/excluir
  ["eventCreated", "eventUpdated", "eventDeleted"].forEach(eventName => {
    document.body.addEventListener(eventName, function () {
      if (window.weddingApp.currentCalendar) {
        window.weddingApp.currentCalendar.refetchEvents();
      }

      const modalEl = document.getElementById("form-modal");
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    });
  });

  // Permite fechar modal via evento customizado
  document.body.addEventListener("closeModal", function () {
    const modalEl = document.getElementById("form-modal");
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
  });

})();
