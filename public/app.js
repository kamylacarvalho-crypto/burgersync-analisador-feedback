// BurgerSync - Frontend da Página de Avaliação do Cliente
let currentRating = 5;

document.addEventListener("DOMContentLoaded", () => {
  setupRating();
  setupExampleButtons();
  setupForm();
});

// Configuração das Estrelas de Avaliação
function setupRating() {
  const starBtns = document.querySelectorAll(".star-btn");
  starBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      currentRating = parseInt(btn.getAttribute("data-val"));
      starBtns.forEach((b) => {
        const val = parseInt(b.getAttribute("data-val"));
        if (val <= currentRating) {
          b.classList.add("active");
        } else {
          b.classList.remove("active");
        }
      });
    });
  });
}

// Botões de Exemplo para Teste Rápido
function setupExampleButtons() {
  const btnPos = document.getElementById("btnExPositivo");
  const btnNeu = document.getElementById("btnExNeutro");
  const btnCrit = document.getElementById("btnExCritico");

  btnPos?.addEventListener("click", () => {
    document.getElementById("nome").value = "Camila Ribeiro";
    document.getElementById("contato").value = "(14) 99812-3344";
    document.getElementById("pedido_id").value = "PED-8020";
    document.getElementById("comentario").value = "O Smash Burger com queijo cheddar artesanal estava maravilhoso! Chegou quentinho em 20 minutos na Vila Margarida.";
    setRating(5);
  });

  btnNeu?.addEventListener("click", () => {
    document.getElementById("nome").value = "Felipe Antunes";
    document.getElementById("contato").value = "(14) 99745-6677";
    document.getElementById("pedido_id").value = "PED-8025";
    document.getElementById("comentario").value = "O hambúrguer é bom, mas o refrigerante veio sem canudo e a batata frita estava um pouco murcha.";
    setRating(3);
  });

  btnCrit?.addEventListener("click", () => {
    document.getElementById("nome").value = "Rodrigo Mendes";
    document.getElementById("contato").value = "(14) 99655-9988";
    document.getElementById("pedido_id").value = "PED-8032";
    document.getElementById("comentario").value = "Péssima experiência! O pedido atrasou 1 hora e 45 minutos para entregar no Centro, a comida chegou fria e a maionese parecia estragada. Quero cancelamento e estorno imediato!";
    setRating(1);
  });
}

function setRating(val) {
  currentRating = val;
  const starBtns = document.querySelectorAll(".star-btn");
  starBtns.forEach((b) => {
    const bVal = parseInt(b.getAttribute("data-val"));
    if (bVal <= val) {
      b.classList.add("active");
    } else {
      b.classList.remove("active");
    }
  });
}

// Envio do Formulário
function setupForm() {
  const form = document.getElementById("feedbackForm");
  const btnSubmit = document.getElementById("btnSubmit");
  const resultCard = document.getElementById("resultCard");
  const btnNewFeedback = document.getElementById("btnNewFeedback");

  btnNewFeedback?.addEventListener("click", () => {
    resultCard.style.display = "none";
    form.reset();
    setRating(5);
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const nome = document.getElementById("nome").value.trim();
    const contato = document.getElementById("contato").value.trim();
    const pedido_id = document.getElementById("pedido_id").value.trim();
    const comentario = document.getElementById("comentario").value.trim();

    if (!comentario) {
      showToast("Por favor, preencha o seu comentário.", "error");
      return;
    }

    btnSubmit.disabled = true;
    btnSubmit.innerHTML = `<span>⏳ Processando análise com IA...</span>`;

    const payload = {
      nome,
      contato,
      pedido_id: pedido_id || `PED-${Math.floor(1000 + Math.random() * 9000)}`,
      comentario,
      rating: currentRating
    };

    try {
      // Tenta enviar para o backend Python
      const response = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      displayResult(data.feedback, data.alert);
      showToast("Avaliação enviada e analisada com sucesso!", "success");
    } catch (err) {
      console.warn("Backend local offline ou estático no GitHub Pages. Acionando contingência local de cliente:", err);
      // Contingência determinística no cliente para garantir funcionamento no GitHub Pages
      const fallbackResult = localClientAnalysis(payload);
      displayResult(fallbackResult.feedback, fallbackResult.alert);
      showToast("Avaliação analisada via contingência client-side!", "success");
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = `<span>🚀 Enviar Avaliação para Análise</span>`;
    }
  });
}

function displayResult(feedback, alertInfo) {
  const resultCard = document.getElementById("resultCard");
  const resBadge = document.getElementById("resBadge");
  const resSummaryText = document.getElementById("resSummaryText");
  const resTags = document.getElementById("resTags");
  const resAlertBox = document.getElementById("resAlertBox");

  // Configura Badge de Sentimento
  resBadge.className = `badge badge-${feedback.sentiment.toLowerCase()}`;
  resBadge.textContent = feedback.sentiment;

  // Resumo
  resSummaryText.textContent = feedback.resumo || "Avaliação processada com sucesso.";

  // Tags
  resTags.innerHTML = "";
  (feedback.tags || ["Geral"]).forEach((tag) => {
    const span = document.createElement("span");
    span.className = "badge badge-tag";
    span.textContent = `#${tag}`;
    resTags.appendChild(span);
  });

  // Caixa de Alerta se Crítico
  if (feedback.sentiment === "Crítico" || feedback.alert_required) {
    resAlertBox.style.display = "flex";
  } else {
    resAlertBox.style.display = "none";
  }

  resultCard.style.display = "block";
  resultCard.scrollIntoView({ behavior: "smooth" });
}

// Motor de Contingência Client-Side (para hospedagem estática no GitHub Pages)
function localClientAnalysis(payload) {
  const text = payload.comentario.toLowerCase();
  const critWords = ["pessimo", "péssimo", "horrivel", "horrível", "frio", "gelado", "cru", "crua", "estragad", "podre", "demorou", "atraso", "reembolso", "nojo", "nunca mais", "lixo"];
  const posWords = ["maravilhoso", "delicia", "delícia", "otimo", "ótimo", "perfeito", "incrivel", "suculento", "muito bom", "gostoso", "rapido", "quentinho", "top", "show"];

  const hasCrit = critWords.some((w) => text.includes(w));
  const hasPos = posWords.some((w) => text.includes(w));

  let sentiment = "Neutro";
  let score = 0.5;
  let alert_required = false;

  if (hasCrit) {
    sentiment = "Crítico";
    score = 0.15;
    alert_required = true;
  } else if (hasPos || payload.rating >= 4) {
    sentiment = "Positivo";
    score = 0.95;
  }

  const tags = [];
  if (text.includes("sabor") || text.includes("lanche") || text.includes("burger") || text.includes("carne") || text.includes("maionese")) tags.push("Sabor");
  if (text.includes("entrega") || text.includes("motoboy") || text.includes("demor") || text.includes("tempo") || text.includes("chegou")) tags.push("Entrega");
  if (text.includes("atend") || text.includes("garcom") || text.includes("whatsapp")) tags.push("Atendimento");
  if (text.includes("frio") || text.includes("quente") || text.includes("quentinho")) tags.push("Temperatura");
  if (tags.length === 0) tags.push("Geral");

  const feedback = {
    id: `FB-${Date.now().toString().slice(-4)}`,
    timestamp: new Date().toISOString(),
    nome: payload.nome,
    contato: payload.contato,
    pedido_id: payload.pedido_id,
    comentario: payload.comentario,
    sentiment,
    score,
    tags,
    resumo: sentiment === "Crítico" ? "Crise operacional reportada pelo cliente com solicitação de providências." : (sentiment === "Positivo" ? "Elogio enfático ao sabor e experiência geral." : "Feedback com observações moderadas."),
    status: "pendente",
    alert_required,
    treated_at: null,
    engine: "client_fallback"
  };

  // Salva no localStorage para sincronizar com o admin no GitHub Pages
  try {
    const existing = JSON.parse(localStorage.getItem("burgersync_feedbacks") || "[]");
    existing.unshift(feedback);
    localStorage.setItem("burgersync_feedbacks", JSON.stringify(existing));
  } catch (e) {
    console.error("Erro localStorage:", e);
  }

  return {
    feedback,
    alert: alert_required ? { alert_sent: true, method: "client_storage_log" } : null
  };
}

// Sistema de Notificações Toast
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
  }, 4000);
}
