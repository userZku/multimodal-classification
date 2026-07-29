const examplePayload = {
  usager_id: "U_TEST_001",
  age: 36,
  niveau_diplome: "Bac+2",
  anciennete_poste_ans: 4,
  code_rome_vise: "M1602",
  departement_insee: "75",
  est_allocataire: 1,
  nationalite_hors_ue: 0,
  synthese_entretien: "Motivation stable, projet cohérent, recherche active.",
};

const statusLabels = {
  ok: "Validation automatique",
  a_revoir: "Revue humaine recommandée",
  error: "Erreur de traitement",
};

const classLabels = {
  0: "Rapide (< 6 mois)",
  1: "Moyen (6 à 12 mois)",
  2: "Risque longue durée (> 12 mois)",
};

const form = document.getElementById("predict-form");
const fillExampleButton = document.getElementById("fill-example");
const healthDot = document.getElementById("health-dot");
const healthLabel = document.getElementById("health-label");
const modelLoaded = document.getElementById("model-loaded");
const modelVersion = document.getElementById("model-version");
const resultEmpty = document.getElementById("result-empty");
const resultCard = document.getElementById("result-card");
const errorBox = document.getElementById("error-box");
const historyList = document.getElementById("history-list");
const historyEmpty = document.getElementById("history-empty");
const refreshHistoryButton = document.getElementById("refresh-history");
const retrainButton = document.getElementById("retrain-button");
const retrainFeedback = document.getElementById("retrain-feedback");

function normalizeRomeCode(value) {
  return (value || "").trim().toUpperCase();
}

function hydrateForm(values) {
  Object.entries(values).forEach(([key, value]) => {
    const field = form.elements.namedItem(key);
    if (!field) {
      return;
    }
    field.value = value;
  });
}

function setHealthState(ok, message, loaded, version, runId) {
  healthDot.classList.remove("ok", "error");
  healthDot.classList.add(ok ? "ok" : "error");
  healthLabel.textContent = message;
  modelLoaded.textContent = loaded;
  modelVersion.textContent = version;

  retrainFeedback.classList.remove("hidden");
  retrainFeedback.textContent = `Run courant: ${runId || "-"}`;
}

async function loadHealth() {
  try {
    const response = await fetch("/health");
    const data = await response.json();
    setHealthState(
      response.ok,
      response.ok ? "Service disponible" : "Service indisponible",
      data.model_loaded ? "Oui" : "Non",
      data.model_version || "-",
      data.run_id || "-"
    );
  } catch (error) {
    setHealthState(false, "Échec de connexion API", "-", "-", "-");
  }
}

function showError(message) {
  resultCard.classList.add("hidden");
  resultCard.classList.remove("alert");
  resultEmpty.classList.add("hidden");
  errorBox.classList.remove("hidden");
  errorBox.textContent = message;
}

function showResult(data) {
  const statusBadge = document.getElementById("result-status");
  const normalizedStatus = String(data.status || "").trim().toLowerCase();

  errorBox.classList.add("hidden");
  resultEmpty.classList.add("hidden");
  resultCard.classList.remove("hidden");
  resultCard.classList.remove("ok", "alert");
  if (normalizedStatus === "ok") {
    resultCard.classList.add("ok");
  } else if (normalizedStatus === "a_revoir") {
    resultCard.classList.add("alert");
  }
  statusBadge.classList.remove("ok", "alert");
  if (normalizedStatus === "ok") {
    statusBadge.classList.add("ok");
  } else if (normalizedStatus === "a_revoir") {
    statusBadge.classList.add("alert");
  }
  statusBadge.textContent = normalizedStatus || data.status;
  const classLabel = classLabels[data.prediction] || "Classe inconnue";
  document.getElementById("result-prediction").innerHTML =
    `<span class="prediction-main">Classe ${data.prediction}</span>` +
    `<span class="prediction-sub">${classLabel}</span>`;
  document.getElementById("result-confidence").textContent = `${Math.round(data.confidence * 100)}%`;
  document.getElementById("result-status-label").textContent =
    statusLabels[normalizedStatus] || data.status;
  document.getElementById("result-request-id").textContent = data.request_id;
  document.getElementById("result-model-version").textContent = data.model_version;
}

function toShortDate(isoString) {
  if (!isoString) {
    return "-";
  }
  const d = new Date(isoString);
  if (Number.isNaN(d.getTime())) {
    return isoString;
  }
  return d.toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderHistory(items) {
  if (!Array.isArray(items) || items.length === 0) {
    historyList.innerHTML = "";
    historyList.classList.add("hidden");
    historyEmpty.classList.remove("hidden");
    return;
  }

  historyEmpty.classList.add("hidden");
  historyList.classList.remove("hidden");

  const rows = [...items].reverse().map((event) => {
    const output = event.output || {};
    const status = output.status || "-";
    const statusClass =
      status === "ok" ? "ok" : status === "a_revoir" ? "a_revoir" : "";
    const prediction = output.prediction ?? "-";
    const classLabel =
      typeof output.prediction === "number"
        ? classLabels[output.prediction] || "Classe inconnue"
        : "Classe inconnue";
    const confidencePct =
      typeof output.confidence === "number"
        ? `${Math.round(output.confidence * 100)}%`
        : "-";

    return `
      <li class="history-item">
        <div class="history-top">
          <span class="history-date">${toShortDate(event.timestamp_utc)}</span>
          <span class="history-status ${statusClass}">${status}</span>
        </div>
        <div class="history-main">Classe ${prediction} - ${classLabel} · Confiance ${confidencePct}</div>
        <div class="history-id">${event.request_id || "-"}</div>
      </li>
    `;
  });

  historyList.innerHTML = rows.join("");
}

async function loadHistory() {
  try {
    const response = await fetch("/history?limit=6");
    if (!response.ok) {
      renderHistory([]);
      return;
    }
    const data = await response.json();
    renderHistory(data.items || []);
  } catch (error) {
    renderHistory([]);
  }
}

async function triggerRetrain() {
  retrainButton.disabled = true;
  retrainFeedback.classList.remove("hidden");
  retrainFeedback.textContent = "Retrain en cours...";

  try {
    const response = await fetch("/retrain", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ trigger: "ui_manual" }),
    });

    const data = await response.json();
    if (!response.ok) {
      retrainFeedback.textContent = data.detail || "Échec du retrain";
      return;
    }

    retrainFeedback.textContent = `Retrain OK (${data.event_id}) - run: ${data.run_id || "-"}`;
    await loadHealth();
  } catch (error) {
    retrainFeedback.textContent = "Erreur de connexion retrain";
  } finally {
    retrainButton.disabled = false;
  }
}

function serializePayload() {
  const formData = new FormData(form);
  const romeCode = normalizeRomeCode(formData.get("code_rome_vise")) || null;

  return {
    usager_id: formData.get("usager_id") || null,
    age: Number(formData.get("age")),
    niveau_diplome: formData.get("niveau_diplome") || null,
    anciennete_poste_ans: Number(formData.get("anciennete_poste_ans")),
    code_rome_vise: romeCode,
    departement_insee: formData.get("departement_insee") || null,
    est_allocataire: Number(formData.get("est_allocataire")),
    nationalite_hors_ue: Number(formData.get("nationalite_hors_ue")),
    synthese_entretien: formData.get("synthese_entretien") || "",
  };
}

fillExampleButton.addEventListener("click", () => {
  hydrateForm(examplePayload);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.classList.add("hidden");

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(serializePayload()),
    });

    const data = await response.json();
    if (!response.ok) {
      showError(data.detail || "Erreur inconnue pendant la prédiction.");
      return;
    }

    showResult(data);
    loadHistory();
  } catch (error) {
    showError("Impossible de joindre l'API de prédiction.");
  }
});

refreshHistoryButton.addEventListener("click", () => {
  loadHistory();
});

retrainButton.addEventListener("click", () => {
  triggerRetrain();
});

hydrateForm(examplePayload);
loadHealth();
loadHistory();