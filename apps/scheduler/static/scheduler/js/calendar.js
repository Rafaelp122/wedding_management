(function () {
  window.weddingApp = window.weddingApp || {};
  window.weddingApp.currentCalendar = null;

  document.addEventListener("htmx:afterSwap", function (event) {
    if (event.detail.target.id === "tab-scheduler") {
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

          /* ---------------------------------------------------
             EVENTO COMO RETÂNGULO COLORIDO + TOOLTIP
          ---------------------------------------------------- */
          eventDidMount: function (info) {
            // Cor suave aleatória
            const color = `hsl(${Math.floor(Math.random() * 360)}, 70%, 80%)`;

            info.el.style.backgroundColor = color;
            info.el.style.borderColor = color;

            // Tooltip com título + descrição + horário
            let tooltip = info.event.title || "";

            if (info.event.extendedProps.description) {
              tooltip += "\n" + info.event.extendedProps.description;
            }

            if (info.event.start) {
              const time = info.event.start.toLocaleTimeString("pt-BR", {
                hour: "2-digit",
                minute: "2-digit",
              });
              tooltip += "\n" + time;
            }

            info.el.setAttribute("title", tooltip);
          },

          /* Criar novo evento */
          dateClick: function (info) {
            const modalEl = document.getElementById("form-modal");
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

            htmx.ajax("GET",
              `/scheduler/partial/${weddingId}/event/new/?date=${info.dateStr}`,
              { target: "#form-modal-container", swap: "innerHTML" }
            );

            modal.show();
          },

          /* Editar evento */
          eventClick: function (info) {
            const modalEl = document.getElementById("form-modal");
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

            htmx.ajax("GET",
              `/scheduler/partial/${weddingId}/event/${info.event.id}/edit/`,
              { target: "#form-modal-container", swap: "innerHTML" }
            );

            modal.show();
          },
        });

        calendar.render();
        window.weddingApp.currentCalendar = calendar;
      }, 100);
    }
  });

  /* Ajusta tamanho ao trocar de aba */
  document.addEventListener("click", function (e) {
    const tabLink = e.target.closest('a[data-tab="scheduler"]');
    if (tabLink && window.weddingApp.currentCalendar) {
      setTimeout(() => {
        window.weddingApp.currentCalendar.updateSize();
      }, 100);
    }
  });

  /* Atualiza eventos no CRUD */
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

  /* Fechar modal manual */
  document.body.addEventListener("closeModal", function () {
    const modalEl = document.getElementById("form-modal");
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
  });

})();
