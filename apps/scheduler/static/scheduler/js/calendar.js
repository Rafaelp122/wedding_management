// v21 - FullCalendar + HTMX integração estável
(function() {
  console.log("LOG v21: calendar.js carregado (modo global compatível com HTMX).");
  document.readyState === "complete"
  ? console.log("LOG v21: script pronto para eventos scheduler:loaded.")
  : window.addEventListener("load", () => console.log("LOG v21: DOM totalmente carregado."))

  const calendarSelector = "#calendar";
  const weddingIdSelector = "#wedding-id-data";

  // Lê o ID do casamento do DOM
  function readWeddingId() {
    try {
      const el = document.querySelector(weddingIdSelector);
      if (!el) return null;
      return JSON.parse(el.textContent);
    } catch (e) {
      console.error("ERRO v21: Falha ao ler wedding-id-data:", e);
      return null;
    }
  }

  // Destroi o calendário antigo
  function destroyCalendar() {
    if (window.weddingCalendarInstance) {
      try {
        console.log("LOG v21: Destruindo instância anterior do calendário...");
        window.weddingCalendarInstance.destroy();
      } catch (e) {
        console.warn("LOG v21: erro ao destruir instância:", e);
      }
      window.weddingCalendarInstance = null;
    }
  }

  // Inicializa o calendário
  function initializeCalendar() {
    const calendarEl = document.querySelector(calendarSelector);
    if (!calendarEl) {
      console.warn("LOG v21: #calendar não encontrado — abortando init.");
      return;
    }

    const weddingId = readWeddingId();
    if (!weddingId) {
      calendarEl.innerHTML = `<div class="alert alert-danger">Erro: ID do casamento ausente.</div>`;
      return;
    }

    console.log("LOG v21: Inicializando calendário para weddingId =", weddingId);
    destroyCalendar();

    const calendar = new FullCalendar.Calendar(calendarEl, {
      locale: "pt-br",
      initialView: "dayGridMonth",
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek"
      },
      events: `/scheduler/api/events/${weddingId}/`,

      eventContent(arg) {
        const e = arg.event;
        const props = e.extendedProps || {};

        // Casamento especial
        if (props.isWeddingDay) {
          const coupleNames = e.title || "Casamento";
          return {
            html: `
              <div class="fc-event-wedding">
                <div class="couple-names">${coupleNames}</div>
                <div class="heart">❤️</div>
              </div>
            `
          };
        }

        // Eventos normais (retângulo roxo)
        const time = e.start
          ? e.start.toLocaleTimeString("pt-BR", {
              hour: "2-digit",
              minute: "2-digit",
              hour12: false
            })
          : "";

        return {
          html: `
            <div class="fc-event-main-frame">
              <span class="fc-event-time">${time}</span>
              <span class="fc-event-title">${e.title}</span>
            </div>
          `
        };
      },


      eventDidMount(info) {
        const props = info.event.extendedProps || {};
        if (props.isWeddingDay) info.el.classList.add("fc-event-wedding-day");
        if (props.isCurrentWedding) info.el.classList.add("fc-event-current");

        if (typeof tippy !== "undefined" && !props.isWeddingDay) {
          const tooltip = `
            <strong>${info.event.title}</strong><br>
            ${info.event.start ? info.event.start.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" }) : ""}
            ${info.event.end ? " - " + info.event.end.toLocaleString("pt-BR", { timeStyle: "short" }) : ""}
            ${props.type ? "<br>Tipo: " + props.type : ""}
            ${props.location ? "<br>Local: " + props.location : ""}
            ${props.description ? "<hr><small>" + props.description + "</small>" : ""}
          `;
          tippy(info.el, { content: tooltip, allowHTML: true, theme: "light-border" });
        }
      },

      dateClick(info) {
        console.log("LOG v21: dateClick em", info.dateStr);
        const modalEl = document.getElementById("main-modal");
        if (!modalEl) return;
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        htmx.ajax("GET", `/scheduler/manage/${weddingId}/?action=get_create_form&date=${info.dateStr}`, {
          target: "#modal-container",
          swap: "innerHTML"
        }).then(() => modal.show());
      },

      eventClick(info) {
        if (info.event.extendedProps.isWeddingDay) return;
        const modalEl = document.getElementById("main-modal");
        if (!modalEl) return;
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        htmx.ajax("GET", `/scheduler/manage/${weddingId}/?action=get_edit_form&event_id=${info.event.id}`, {
          target: "#modal-container",
          swap: "innerHTML"
        }).then(() => modal.show());
      },

      editable: true,

      eventDrop(info) {
        sendCalendarUpdate({
          action: "move_resize",
          event_id: info.event.id,
          start_time: info.event.start.toISOString(),
          end_time: info.event.end ? info.event.end.toISOString() : null
        }, info);
      },

      eventResize(info) {
        sendCalendarUpdate({
          action: "move_resize",
          event_id: info.event.id,
          start_time: info.event.start.toISOString(),
          end_time: info.event.end ? info.event.end.toISOString() : null
        }, info);
      }
    });

    calendar.render();
    window.weddingCalendarInstance = calendar;

    // força reposicionamento após HTMX
    setTimeout(() => calendar.updateSize(), 200);
  }

  // Função global para o modal
  window.sendCalendarUpdate = function(data, info) {
    const weddingId = readWeddingId();
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]")?.value;
    if (!csrf || !weddingId) {
      alert("Erro: CSRF ou WeddingId ausente.");
      if (info && info.revert) info.revert();
      return;
    }

    fetch(`/scheduler/manage/${weddingId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf
      },
      body: JSON.stringify(data)
    })
      .then(res => res.json())
      .then(result => {
        if (result.status === "success" && window.weddingCalendarInstance) {
          window.weddingCalendarInstance.refetchEvents();
        } else {
          throw new Error(result.message || "Erro desconhecido.");
        }
        const modalEl = document.getElementById("main-modal");
        if (modalEl) {
          const modal = bootstrap.Modal.getInstance(modalEl);
          if (modal) modal.hide();
        }
      })
      .catch(err => {
        console.error("ERRO v21:", err);
        alert("Falha ao salvar/atualizar evento.");
        if (info && info.revert) info.revert();
      });
  };

  // Quando o partial HTMX for carregado
  document.addEventListener("scheduler:loaded", function() {
    console.log("LOG v21: Evento scheduler:loaded recebido — inicializando calendário.");
    initializeCalendar();
  });

  // Antes de trocar conteúdo da aba do calendário
  document.body.addEventListener("htmx:beforeSwap", e => {
    if (e.target && e.target.id === "tab-scheduler") {
      destroyCalendar();
    }
  });

})();
