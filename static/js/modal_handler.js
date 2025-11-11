// =============================================================
// MODAL HANDLER GLOBAL (HTMX + BOOTSTRAP + FULLCALENDAR)
// =============================================================

// Fecha modais globais após atualização de listas padrão
document.body.addEventListener("listUpdated", () => closeAnyModal());

// 🔹 Escuta o evento "eventCreated" vindo do backend HTMX
document.body.addEventListener("eventCreated", (e) => {
  console.log("🟢 Evento criado recebido via HTMX:", e.detail);

  // Fecha o modal de criação
  closeAnyModal();

  // Atualiza o calendário instantaneamente
  const calendarEl = document.getElementById("calendar");
  if (calendarEl && calendarEl.fullCalendarInstance) {
    const calendar = calendarEl.fullCalendarInstance;

    // Adiciona o evento novo no calendário
    if (e.detail && e.detail.id) {
      calendar.addEvent(e.detail);
      console.log("✅ Evento adicionado no calendário em tempo real!");
    } else {
      console.warn("⚠️ Detalhes do evento ausentes, recarregando eventos...");
      calendar.refetchEvents();
    }
  }
});

// 🔹 Escuta "eventUpdated" para atualizar um evento existente (edição)
document.body.addEventListener("eventUpdated", (e) => {
  console.log("🟠 Evento atualizado via HTMX:", e.detail);

  closeAnyModal();
  const calendarEl = document.getElementById("calendar");
  if (calendarEl && calendarEl.fullCalendarInstance) {
    const event = calendarEl.fullCalendarInstance.getEventById(e.detail.id);
    if (event) {
      event.setProp("title", e.detail.title);
      event.setStart(e.detail.start);
      event.setEnd(e.detail.end);
      event.setExtendedProp("description", e.detail.description);
      console.log("✅ Evento atualizado no calendário instantaneamente!");
    } else {
      console.warn("Evento não encontrado, recarregando todos...");
      calendarEl.fullCalendarInstance.refetchEvents();
    }
  }
});

// 🔹 Escuta "eventDeleted" para remover do calendário
document.body.addEventListener("eventDeleted", (e) => {
  console.log("🔴 Evento removido via HTMX:", e.detail);
  closeAnyModal();
  const calendarEl = document.getElementById("calendar");
  if (calendarEl && calendarEl.fullCalendarInstance) {
    const event = calendarEl.fullCalendarInstance.getEventById(e.detail.id);
    if (event) {
      event.remove();
      console.log("✅ Evento removido instantaneamente do calendário!");
    } else {
      calendarEl.fullCalendarInstance.refetchEvents();
    }
  }
});

// =============================================================
// Funções auxiliares globais
// =============================================================
function closeAnyModal() {
  let modalEl = document.getElementById("form-modal");
  if (!modalEl) modalEl = document.getElementById("delete-modal");

  if (modalEl) {
    const modalInstance = bootstrap.Modal.getInstance(modalEl);
    if (modalInstance) modalInstance.hide();
    cleanupBackdrops();
  }
}

function cleanupBackdrops() {
  const backdrops = document.querySelectorAll(".modal-backdrop");
  backdrops.forEach(b => b.remove());
  document.body.classList.remove("modal-open");
  document.body.style.overflow = "";
}
