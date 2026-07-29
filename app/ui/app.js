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

const form = document.getElementById("predict-form");
const fillExampleButton = document.getElementById("fill-example");
const healthDot = document.getElementById("health-dot");
const healthLabel = document.getElementById("health-label");
const modelLoaded = document.getElementById("model-loaded");
const modelVersion = document.getElementById("model-version");
const resultEmpty = document.getElementById("result-empty");
const resultCard = document.getElementById("result-card");
const errorBox = document.getElementById("error-box");

function hydrateForm(values) {
  Object.entries(values).forEach(([key, value]) => {
    const field = form.elements.namedItem(key);
    if (!field) {
      return;
    }
    field.value = value;
  });
}

function setHealthState(ok, message, loaded, version) {
  healthDot.classList.remove("ok", "error");
  healthDot.classList.add(ok ? "ok" : "error");
  healthLabel.textContent = message;
  modelLoaded.textContent = loaded;
  modelVersion.textContent = version;
}

async function loadHealth() {
  try {
    const response = await fetch("/health");
    const data = await response.json();
    setHealthState(
      response.ok,
      response.ok ? "Service disponible" : "Service indisponible",
      data.model_loaded ? "Oui" : "Non",
      data.model_version || "-"
    );
  } catch (error) {
    setHealthState(false, "Échec de connexion API", "-", "-");
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

  errorBox.classList.add("hidden");
  resultEmpty.classList.add("hidden");
  resultCard.classList.remove("hidden");
  resultCard.classList.toggle("alert", data.status === "a_revoir");
  statusBadge.classList.toggle("alert", data.status === "a_revoir");
  statusBadge.textContent = data.status;
  document.getElementById("result-prediction").textContent = `Classe ${data.prediction}`;
  document.getElementById("result-confidence").textContent = `${Math.round(data.confidence * 100)}%`;
  document.getElementById("result-status-label").textContent =
    statusLabels[data.status] || data.status;
  document.getElementById("result-request-id").textContent = data.request_id;
  document.getElementById("result-model-version").textContent = data.model_version;
}

function serializePayload() {
  const formData = new FormData(form);
  return {
    usager_id: formData.get("usager_id") || null,
    age: Number(formData.get("age")),
    niveau_diplome: formData.get("niveau_diplome") || null,
    anciennete_poste_ans: Number(formData.get("anciennete_poste_ans")),
    code_rome_vise: formData.get("code_rome_vise") || null,
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
  } catch (error) {
    showError("Impossible de joindre l'API de prédiction.");
  }
});

hydrateForm(examplePayload);
loadHealth();