// BurgerSync - Frontend do Painel Administrativo de Gestão
let currentFeedbacks = [];
let currentFilterSentiment = "todos";
let currentFilterStatus = "todos";
let currentFilterTag = "todas";
let searchQuery = "";

// Dados pré-carregados para contingência no GitHub Pages
const DEFAULT_SEED_DATA = [
  {
    id: "FB-101",
    timestamp: "2026-11-23T14:15:00",
    nome: "Mariana Souza",
    contato: "(14) 99781-4455",
    pedido_id: "PED-7801",
    comentario: "O Burger da Vila com bacon crocante e maionese verde artesanal estava espetacular! Chegou bem quentinho aqui no Jardim Ouro Verde em apenas 22 minutos. Parabéns!",
    sentiment: "Positivo",
    score: 0.98,
    tags: ["Sabor", "Entrega", "Temperatura"],
    resumo: "Elogio enfático ao sabor do lanche, crocância e agilidade na entrega.",
    status: "lido",
    alert_required: false,
    treated_at: "2026-11-23T14:30:00"
  },
  {
    id: "FB-102",
    timestamp: "2026-11-23T14:40:00",
    nome: "Lucas Ferreira",
    contato: "(14) 99123-8877",
    pedido_id: "PED-7815",
    comentario: "Melhor smash burger de Ourinhos! Pão brioche macio, carne super suculenta e atendimento impecável no balcão da loja do Centro.",
    sentiment: "Positivo",
    score: 0.96,
    tags: ["Sabor", "Atendimento"],
    resumo: "Elogio ao hambúrguer smash e excelente atendimento no Centro.",
    status: "lido",
    alert_required: false,
    treated_at: "2026-11-23T14:45:00"
  },
  {
    id: "FB-103",
    timestamp: "2026-11-23T15:05:00",
    nome: "Beatriz Lima",
    contato: "(14) 99654-1122",
    pedido_id: "PED-7830",
    comentario: "O lanche é bem saboroso, mas achei que a porção de batata rústica veio um pouco murcha pelo vapor na embalagem. Talvez um saquinho com respiro ajudaria.",
    sentiment: "Neutro",
    score: 0.55,
    tags: ["Sabor", "Embalagem"],
    resumo: "Lanche aprovado, porém batatas murchas devido à retenção de vapor na embalagem.",
    status: "pendente",
    alert_required: false,
    treated_at: null
  },
  {
    id: "FB-104",
    timestamp: "2026-11-23T15:15:00",
    nome: "Carlos Eduardo Silva",
    contato: "(14) 99876-1234",
    pedido_id: "PED-7842",
    comentario: "Péssima experiência no pedido PED-7842! O pedido demorou quase 2 horas para entregar na Vila Odilon, o hambúrguer veio completamente gelado e a carne estava crua no meio. Exijo estorno ou providências urgentes!",
    sentiment: "Crítico",
    score: 0.10,
    tags: ["Entrega", "Temperatura", "Sabor"],
    resumo: "Crise de entrega com 2h de atraso, comida gelada e carne malpassada/crua.",
    status: "pendente",
    alert_required: true,
    treated_at: null
  },
  {
    id: "FB-105",
    timestamp: "2026-11-23T15:20:00",
    nome: "Patrícia Mendes",
    contato: "(14) 99745-9900",
    pedido_id: "PED-7850",
    comentario: "Encontrei um cabelo grudado no queijo derretido do meu hambúrguer! Uma falta de higiene inaceitável. Quero o reembolso imediato via PIX.",
    sentiment: "Crítico",
    score: 0.08,
    tags: ["Higiene", "Sabor"],
    resumo: "Problema grave de higiene com presença de corpo estranho no produto.",
    status: "pendente",
    alert_required: true,
    treated_at: null
  }
];

document.addEventListener("DOMContentLoaded", () => {
  setupFilterControls();
  setupModal();
  loadData();

  document.getElementById("btnRefresh")?.addEventListener("click", () => {
    loadData();
    showToast("Dados atualizados com sucesso!", "info");
  });

  document.getElementById("btnFilterPendingCritical")?.addEventListener("click", () => {
    setFilterSentiment("Crítico");
    setFilterStatus("pendente");
  });
});

// Configuração dos Botões de Filtro e Busca
function setupFilterControls() {
  // Filtro por Sentimento
  const sentimentBtns = document.querySelectorAll('[data-filter-type="sentiment"]');
  sentimentBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      sentimentBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilterSentiment = btn.getAttribute("data-value");
      applyFiltersAndRender();
    });
  });

  // Filtro por Status
  const statusBtns = document.querySelectorAll('[data-filter-type="status"]');
  statusBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      statusBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilterStatus = btn.getAttribute("data-value");
      applyFiltersAndRender();
    });
  });

  // Filtro por Tag
  const selectTag = document.getElementById("selectTagFilter");
  selectTag?.addEventListener("change", (e) => {
    currentFilterTag = e.target.value;
    applyFiltersAndRender();
  });

  // Busca textual
  const searchInput = document.getElementById("searchInput");
  searchInput?.addEventListener("input", (e) => {
    searchQuery = e.target.value.toLowerCase().trim();
    applyFiltersAndRender();
  });
}

function setFilterSentiment(sentiment) {
  currentFilterSentiment = sentiment;
  const btns = document.querySelectorAll('[data-filter-type="sentiment"]');
  btns.forEach((b) => {
    if (b.getAttribute("data-value") === sentiment) b.classList.add("active");
    else b.classList.remove("active");
  });
  applyFiltersAndRender();
}

function setFilterStatus(status) {
  currentFilterStatus = status;
  const btns = document.querySelectorAll('[data-filter-type="status"]');
  btns.forEach((b) => {
    if (b.getAttribute("data-value") === status) b.classList.add("active");
    else b.classList.remove("active");
  });
  applyFiltersAndRender();
}

// Carregamento de Dados da API (ou fallback client-side)
async function loadData() {
  try {
    const res = await fetch("/api/feedbacks");
    if (!res.ok) throw new Error("Erro na API");
    const data = await res.json();
    currentFeedbacks = data;
  } catch (err) {
    console.warn("Backend offline ou rodando em GitHub Pages. Carregando dados locais:", err);
    // Recupera dados salvos localmente ou padrão
    const localSaved = JSON.parse(localStorage.getItem("burgersync_feedbacks") || "[]");
    currentFeedbacks = [...localSaved, ...DEFAULT_SEED_DATA];
    // Remove duplicatas de IDs
    const seen = new Set();
    currentFeedbacks = currentFeedbacks.filter((item) => {
      if (seen.has(item.id)) return false;
      seen.add(item.id);
      return true;
    });
  }

  updateMetrics();
  applyFiltersAndRender();
}

// Atualização dos Cards de Métricas
function updateMetrics() {
  const total = currentFeedbacks.length;
  const positivos = currentFeedbacks.filter((fb) => fb.sentiment === "Positivo").length;
  const neutros = currentFeedbacks.filter((fb) => fb.sentiment === "Neutro").length;
  const criticos = currentFeedbacks.filter((fb) => fb.sentiment === "Crítico").length;
  const criticosPendentes = currentFeedbacks.filter((fb) => fb.sentiment === "Crítico" && fb.status === "pendente").length;
  const satisfacao = total > 0 ? Math.round((positivos / total) * 100) : 0;

  document.getElementById("metricTotal").textContent = total;
  document.getElementById("metricSatisfacao").textContent = `${satisfacao}%`;
  document.getElementById("metricPositivosSub").textContent = `${positivos} de ${total} avaliações`;
  document.getElementById("metricNeutros").textContent = neutros;
  document.getElementById("metricCriticosPendentes").textContent = criticosPendentes;
  document.getElementById("metricCriticosTotal").textContent = `de ${criticos} críticas totais`;

  // Banner de Alerta Crítico
  const alertBanner = document.getElementById("criticalAlertBanner");
  const alertText = document.getElementById("criticalAlertText");
  if (criticosPendentes > 0) {
    alertBanner.style.display = "flex";
    alertText.textContent = `Existe(m) ${criticosPendentes} caso(s) crítico(s) aguardando tratativa urgente de gerência!`;
  } else {
    alertBanner.style.display = "none";
  }
}

// Filtros e Renderização da Lista
function applyFiltersAndRender() {
  let list = [...currentFeedbacks];

  if (currentFilterSentiment !== "todos") {
    list = list.filter((fb) => fb.sentiment.toLowerCase() === currentFilterSentiment.toLowerCase());
  }

  if (currentFilterStatus !== "todos") {
    list = list.filter((fb) => fb.status.toLowerCase() === currentFilterStatus.toLowerCase());
  }

  if (currentFilterTag !== "todas") {
    list = list.filter((fb) => (fb.tags || []).some((t) => t.toLowerCase() === currentFilterTag.toLowerCase()));
  }

  if (searchQuery) {
    list = list.filter((fb) => {
      return (
        fb.nome?.toLowerCase().includes(searchQuery) ||
        fb.pedido_id?.toLowerCase().includes(searchQuery) ||
        fb.comentario?.toLowerCase().includes(searchQuery) ||
        fb.contato?.toLowerCase().includes(searchQuery)
      );
    });
  }

  renderFeedbackList(list);
}

function renderFeedbackList(list) {
  const container = document.getElementById("feedbackList");
  const counter = document.getElementById("feedbackCounter");
  counter.textContent = `Exibindo ${list.length} de ${currentFeedbacks.length} avaliações`;

  container.innerHTML = "";

  if (list.length === 0) {
    container.innerHTML = `
      <div class="card" style="text-align: center; padding: 3rem 1rem;">
        <span style="font-size: 2.5rem; display: block; margin-bottom: 0.5rem;">🔍</span>
        <h3 style="color: var(--text-primary); margin-bottom: 0.25rem;">Nenhuma avaliação encontrada</h3>
        <p style="color: var(--text-muted); font-size: 0.9rem;">Tente ajustar os filtros ou o termo de busca.</p>
      </div>
    `;
    return;
  }

  list.forEach((fb) => {
    const isCritico = fb.sentiment === "Crítico";
    const isTreated = fb.status === "lido";
    const dateFormatted = new Date(fb.timestamp).toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    });

    // Formata telefone para WhatsApp (apenas números com 55)
    const rawPhone = (fb.contato || "").replace(/\D/g, "");
    const waUrl = rawPhone.length >= 10 ? `https://wa.me/55${rawPhone}?text=Ol%C3%A1%20${encodeURIComponent(fb.nome)},%20sou%20o%20gerente%20do%20BurgerSync%20Ourinhos%20sobre%20seu%20pedido%20${encodeURIComponent(fb.pedido_id)}` : "#";

    const card = document.createElement("div");
    card.className = `feedback-card is-${fb.sentiment.toLowerCase()}`;
    card.id = `card-${fb.id}`;

    card.innerHTML = `
      <div class="feedback-header">
        <div class="client-info">
          <h4>${escapeHtml(fb.nome)}</h4>
          <div class="client-meta">
            <span>📦 ${escapeHtml(fb.pedido_id)}</span>
            <span>📱 ${escapeHtml(fb.contato)}</span>
            <span>🕒 ${dateFormatted}</span>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span class="badge badge-${fb.sentiment.toLowerCase()}">${fb.sentiment}</span>
        </div>
      </div>

      <div class="feedback-body">
        "${escapeHtml(fb.comentario)}"
      </div>

      ${fb.resumo ? `
      <div class="feedback-summary">
        <span>💡 <strong>IA:</strong> ${escapeHtml(fb.resumo)}</span>
      </div>
      ` : ""}

      <div class="feedback-footer">
        <div class="tags-list">
          ${(fb.tags || []).map((t) => `<span class="badge badge-tag">#${escapeHtml(t)}</span>`).join("")}
        </div>

        <div class="feedback-actions">
          ${rawPhone.length >= 10 ? `
          <a href="${waUrl}" target="_blank" rel="noopener noreferrer" class="btn-whatsapp" title="Conversar no WhatsApp">
            <span>💬</span> WhatsApp
          </a>
          ` : ""}

          <label class="checkbox-treated">
            <input type="checkbox" ${isTreated ? "checked" : ""} data-id="${fb.id}">
            <span>${isTreated ? "Tratada / Lida" : "Marcar como tratada"}</span>
          </label>
        </div>
      </div>
    `;

    // Event listener para o checkbox de status
    const checkbox = card.querySelector('input[type="checkbox"]');
    checkbox.addEventListener("change", async (e) => {
      const newStatus = e.target.checked ? "lido" : "pendente";
      await toggleStatus(fb.id, newStatus);
    });

    container.appendChild(card);
  });
}

// Alteração de Status com Sincronização
async function toggleStatus(feedbackId, newStatus) {
  try {
    const res = await fetch(`/api/feedback/${feedbackId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });

    if (!res.ok) throw new Error("Falha no servidor");
    const updated = await res.json();
    updateLocalFeedbackState(feedbackId, newStatus);
    showToast(`Status atualizado para ${newStatus === "lido" ? "Tratada" : "Pendente"}!`, "success");
  } catch (err) {
    console.warn("Backend offline, atualizando estado no cliente:", err);
    updateLocalFeedbackState(feedbackId, newStatus);
    showToast(`Status salvo localmente (${newStatus === "lido" ? "Tratada" : "Pendente"})!`, "success");
  }
}

function updateLocalFeedbackState(feedbackId, newStatus) {
  const item = currentFeedbacks.find((fb) => fb.id === feedbackId);
  if (item) {
    item.status = newStatus;
    item.treated_at = newStatus === "lido" ? new Date().toISOString() : null;
    try {
      localStorage.setItem("burgersync_feedbacks", JSON.stringify(currentFeedbacks));
    } catch (e) {}
  }
  updateMetrics();
  applyFiltersAndRender();
}

// Modal do Log de Alertas (.tmp/alerts.log)
function setupModal() {
  const modal = document.getElementById("alertsModal");
  const btnOpen = document.getElementById("btnOpenAlertsLog");
  const btnClose = document.getElementById("btnCloseModal");
  const btnCloseFooter = document.getElementById("btnCloseModalFooter");
  const logContent = document.getElementById("logContent");

  btnOpen?.addEventListener("click", async () => {
    modal.classList.add("active");
    logContent.textContent = "Carregando registros do arquivo .tmp/alerts.log...";

    try {
      const res = await fetch("/api/alerts");
      if (!res.ok) throw new Error("Falha ao buscar alertas");
      const data = await res.json();
      if (data.alerts && data.alerts.length > 0) {
        logContent.textContent = data.alerts.join("\n\n--------------------------------------------------------------------------------\n\n");
      } else {
        logContent.textContent = "[INFO] Nenhum alerta crítico registrado até o momento.";
      }
    } catch (e) {
      logContent.textContent = `================================================================================\n[ALERTA CRÍTICO GERENCIAL] Modo de Contingência\nNenhum alerta pendente no momento.\n================================================================================`;
    }
  });

  const closeModal = () => modal.classList.remove("active");
  btnClose?.addEventListener("click", closeModal);
  btnCloseFooter?.addEventListener("click", closeModal);
  modal?.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === "success" ? "✅" : (type === "error" ? "❌" : "ℹ️")}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
