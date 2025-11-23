(function () {
  // =============================================================
  // CONTROLES DO CALENDÁRIO
  // =============================================================
  // 
  // Este script ESPERA que 'window.logger' exista
  // (definido no template _base.html).
  //
  // =============================================================

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
    if (window.weddingApp.currentCalendar) {
      logger.log("🗓️ Instância do calendário já existe, ignorando 'afterSwap'.");
      return;
    }

    logger.log("🗓️ HTMX 'afterSwap' detetado para #tab-scheduler. Inicializando calendário...");

    // Timeout para garantir que o DOM está pronto e as bibliotecas carregadas
    setTimeout(function () {
      const calendarEl = document.getElementById("calendar");
      if (!calendarEl) {
        logger.error("❌ Falha ao inicializar: elemento #calendar não encontrado no DOM.");
        return;
      }

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
          // (Não colocamos logs aqui, pois é muito "barulhento" - executa para cada evento)
          const color = getEventColor(info.event.id);
          info.el.style.backgroundColor = color;
          info.el.style.borderColor = color;

          let tooltip = `Título: ${info.event.title || "—"}`;
          // ... (resto do seu código de tooltip, está ótimo) ...
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
          logger.log("➕ Abrindo modal: Criar Evento (dateClick)");
          const modalEl = document.getElementById("form-modal");
          const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

          htmx.ajax(
            "GET",
            `/scheduler/partial/${weddingId}/event/new/?date=${info.dateStr}`,
            { target: "#form-modal-container", swap: "innerHTML" }
          );

          modal.show();
        },

        // Visualizar detalhes do evento
        eventClick: function (info) {
          logger.log(`👁️ Abrindo modal: Detalhes do Evento ID: ${info.event.id}`);
          const modalEl = document.getElementById("form-modal");
          const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

          htmx.ajax(
            "GET",
            `/scheduler/partial/${weddingId}/event/${info.event.id}/detail/`,
            { target: "#form-modal-container", swap: "innerHTML" }
          );

          modal.show();
        },
      });

      calendar.render();
      
      // Guarda a instância globalmente para o 'modal_handler' poder usá-la
      window.weddingApp.currentCalendar = calendar;
      calendarEl.fullCalendarInstance = calendar; // Dupla garantia
      
      logger.log("✅ Calendário inicializado e renderizado com sucesso!");

    }, 100); // O timeout de 100ms é uma boa prática
  });

  // Atualiza tamanho ao trocar aba
  document.addEventListener("click", function (e) {
    const tab = e.target.closest('a[data-tab="scheduler"]');
    if (!tab || !window.weddingApp.currentCalendar) return;

    logger.log("🔄 Clicou na aba Calendário, atualizando 'updateSize()'.");
    setTimeout(() => {
      window.weddingApp.currentCalendar.updateSize();
    }, 100);
  });
  
  // Fechar modal via evento customizado (do HTMX)
  // Este listener PODE ficar, pois é genérico.
  document.body.addEventListener("closeModal", function () {
    const modalEl = document.getElementById("form-modal");
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) {
      logger.log("Event 'closeModal' recebido. Fechando modal.");
      modal.hide();
    }
  });

  // Listener para refetch após salvar evento
  document.body.addEventListener("eventSaved", function () {
    logger.log("🔄 Event 'eventSaved' recebido. Refazendo fetch de eventos.");
    
    if (window.weddingApp.currentCalendar) {
      window.weddingApp.currentCalendar.refetchEvents();
      logger.log("✅ Eventos atualizados no calendário.");
      
      // Fecha o modal após atualizar
      const modalEl = document.getElementById("form-modal");
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) {
        modal.hide();
        logger.log("Modal fechado após salvar evento.");
      }
    }
  });

  // Listener para remover evento deletado do calendário
  document.body.addEventListener("eventDeleted", function (e) {
    const eventId = e.detail?.id;
    if (!eventId || !window.weddingApp.currentCalendar) return;
    
    logger.log(`🗑️ Event 'eventDeleted' recebido. Removendo evento ID: ${eventId}`);
    
    const event = window.weddingApp.currentCalendar.getEventById(eventId);
    if (event) {
      event.remove();
      logger.log(`✅ Evento ${eventId} removido do calendário.`);
    }
    
    // Fecha o modal
    const modalEl = document.getElementById("form-modal");
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) {
      modal.hide();
    }
  });

})();