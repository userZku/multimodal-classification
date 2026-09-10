# Zero-shot CLIP — Mini-cours

> Brief associé : M4-B2 (option C — la plus rapide à mettre en œuvre)
> Durée : ~20 min
> Pré-requis : HuggingFace `transformers` installé.

## Pourquoi cette techno ?

**CLIP** (OpenAI 2021) est un **foundation model** entraîné sur 400 M
paires (image, légende) — il a appris à associer images et descriptions
textuelles.

**Le pouvoir du zero-shot** : tu donnes à CLIP **ton image PCB** + **les
descriptions textuelles** de tes 7 classes (« an image of a PCB with X
defect »), il te retourne la **probabilité** de chaque classe. **Aucun
entraînement.**

**Quand préférer zero-shot** :
- **MVP rapide sans données labellisées**
- Phase exploratoire avant de décider si ça vaut la peine d'annoter
- Cas où les classes sont **bien descriptibles en mots**

**Quand éviter** :
- Domaines ultra-spécifiques (PCB justement — CLIP n'a pas vu des
  millions de PCB pendant pré-entraînement)
- Précision critique (transfer learning fait mieux après fine-tune)
- Production temps réel (latence ~100-200 ms par image)

**Sur PCB Defect** : intéressant comme **baseline ultra-rapide à monter**,
mais probablement **dominé** en précision par transfer learning.

> ⚠️ **À interpréter avec nuance** : un CLIP faible ici **ne veut pas dire
> « CLIP est mauvais »**. C'est un **baseline sémantique** entraîné sur des
> images « du web », pas sur des cartes PCB 64×64 — il n'est **pas adapté à ce
> domaine sans adaptation** (prompts soignés, voire fine-tuning). Le bon message
> de ton verdict : *« CLIP n'est pas le bon outil **pour ce cas précis** »*, pas
> *« CLIP est nul »*. **Aucune des 3 approches n'est universellement meilleure.**

## Concepts clés

### Workflow

```python
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

# 1. Charge CLIP (~150 Mo au 1ᵉʳ appel, cache local ensuite)
MODEL_ID = "openai/clip-vit-base-patch32"
processor = CLIPProcessor.from_pretrained(MODEL_ID)
model = CLIPModel.from_pretrained(MODEL_ID)
model.eval()

# 2. Définit tes prompts (1 par classe)
class_prompts = [
    "a photograph of a clean PCB with no defects",
    "a photograph of a PCB with an open circuit",
    "a photograph of a PCB with a short circuit",
    # ... 1 prompt par classe (7 total)
]

# 3. Charge une image et infère
image = Image.open("data/pcb_defect_sample/short/short_0001.png").convert("RGB")
inputs = processor(text=class_prompts, images=image, return_tensors="pt", padding=True)

with torch.no_grad():
    outputs = model(**inputs)

logits = outputs.logits_per_image  # (1, 7)
probs = logits.softmax(dim=1)[0]
predicted_class = class_prompts[probs.argmax()]
print(f"Predicted: {predicted_class}, confidence: {probs.max():.3f}")
```

### L'art du prompt engineering

La **qualité** du zero-shot dépend fortement des prompts. Trois variantes :

```python
# Variante 1 — minimale (souvent insuffisante)
prompts_1 = ["a PCB", "a defective PCB", ...]

# Variante 2 — moyennement spécifique (recommandé)
prompts_2 = [
    "a photograph of a clean PCB with no defects",
    "a photograph of a PCB with an open circuit defect",
    ...
]

# Variante 3 — très spécifique (peut overfit le prompt)
prompts_3 = [
    "a high-resolution photograph of a green PCB with intact copper traces and no visible defects",
    ...
]
```

**Test empirique** : essaie 2-3 variantes de prompts, mesure l'accuracy
sur un échantillon (~50 images), choisis la meilleure.

### Évaluation

Pas de train, mais évaluation **sur le test set** comme les autres
options. Mesure accuracy macro + matrice de confusion (certaines classes
seront naturellement mieux gérées par CLIP que d'autres).

## Exemple minimal qui tourne

CLIP classe **sans aucun entraînement** : on lui donne une image et des
descriptions textuelles, il rend la plus probable. Tout se joue dans les
**mots du prompt**.

```python
# transformers==4.46.0
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

MODEL_ID = "openai/clip-vit-base-patch32"
processor = CLIPProcessor.from_pretrained(MODEL_ID)   # ~150 Mo, CPU OK
model = CLIPModel.from_pretrained(MODEL_ID)

image = Image.open("data/pcb_defect_sample/ok/ok_0000.png").convert("RGB")
labels = [
    "a photo of a clean printed circuit board",
    "a photo of a circuit board with an open circuit",
    "a photo of a circuit board with a short circuit",
]
inputs = processor(text=labels, images=image, return_tensors="pt", padding=True)
with torch.no_grad():
    logits = model(**inputs).logits_per_image     # similarité image ↔ chaque texte
probs = logits.softmax(dim=1)[0]
print(labels[int(probs.argmax())], f"({probs.max():.2f})")
```

Aucun `.fit()`, aucun label d'entraînement : c'est le **zero-shot**. La qualité
dépend entièrement de la formulation des descriptions.

## Exercice guidé

1. Écris une description (prompt) pour **chacune des 7 classes** PCB.
2. Teste CLIP sur **5 images** de classes différentes : combien sont bien
   classées ?
3. Reformule les prompts des classes ratées (ex. *« copper exposure »* vs
   *« a circuit board with excess copper »*) — l'**ingénierie de prompt**
   change-t-elle le résultat ?
4. Conclus : CLIP est-il meilleur sur les défauts **visuellement évidents**
   (open/short) ou **subtils** (mousebite/spur) ? Pourquoi ?

**Attendu** : tu mesures qu'un foundation model donne un résultat **immédiat
sans entraînement**, mais que sa précision sur un domaine technique dépend du
prompt — l'arbitrage à poser face au CNN/transfer (coût zéro entraînement vs
précision moindre sur défauts fins).

## Performance attendue sur PCB

- **Accuracy** : ~30-60 % selon prompts (très variable). PCB étant un
  domaine spécifique, CLIP peut **galérer** sur les défauts subtils
  (`pin_hole`, `spur`).
- **Temps train** : **0** (no train !)
- **Latence inférence** : ~80-200 ms par image (CPU)
- **Mémoire** : ~600 Mo (modèle chargé en RAM)

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Prompts trop vagues | Accuracy basse |
| Prompts en français | CLIP est entraîné majoritairement EN — utilise EN |
| Forgot `image.convert("RGB")` | CLIP attend 3 canaux |
| Comparer 0 % d'accuracy CLIP à 90 % CNN | C'est attendu sur domaines spécifiques — c'est le **point** du verdict |
| Tester sur 5 images et conclure | Test sur ≥ 100 images (échantillon stratifié) |
| Forgot `model.eval()` | Pas critique ici (pas de dropout/batchnorm actif) mais bonne pratique |

## Pour aller plus loin

- **HuggingFace — CLIP overview** : <https://huggingface.co/docs/transformers/model_doc/clip>
- **OpenAI CLIP paper** : <https://arxiv.org/abs/2103.00020>
- **Prompt engineering pour CLIP** : <https://github.com/openai/CLIP/blob/main/notebooks/Prompt_Engineering_for_ImageNet.ipynb>

## Vérification

- [ ] CLIP chargé (`openai/clip-vit-base-patch32`)
- [ ] 7 prompts définis (1 par classe, en EN)
- [ ] Inférence fonctionne sur ≥ 10 images
- [ ] Accuracy mesurée sur un échantillon test (≥ 50 images stratifiées)
- [ ] J'ai compris pourquoi CLIP peut être dominé par transfer learning
      sur un domaine très spécifique
