# Comparaison économique — Mini-cours

> Brief associé : M4-B2
> Durée : ~15 min
> Pré-requis : votre option implémentée.

## Pourquoi cette techno ?

Inès veut **arbitrer** entre 3 approches pour TechniMatic. La précision
seule ne suffit pas — il faut **chiffrer** :

- **Coût d'entraînement** (temps + matériel + € si cloud)
- **Coût d'inférence** (latence + € par requête)
- **Précision attendue** (accuracy, F1, autres)
- **Maintenance** (réentraîner ? quand ?)

Mais tu n'as **implémenté qu'une option**. Comment chiffrer les 2 autres ?

**Méthode** : combine **mesures réelles** (option implémentée) +
**estimations argumentées** (sources publiques, doc HuggingFace, mini-prototypes
de 10 lignes).

## Concepts clés

### Mesurer (option implémentée)

```python
import time

# Temps train
t0 = time.perf_counter()
for epoch in range(EPOCHS):
    train_one_epoch(...)
fit_time = time.perf_counter() - t0

# Latence inférence sur 1 image
t0 = time.perf_counter()
_ = model(X_single)
latency_ms = (time.perf_counter() - t0) * 1000

# Mémoire modèle
torch.save(model.state_dict(), "tmp.pt")
mem_mo = Path("tmp.pt").stat().st_size / 1e6
```

### Estimer (options non implémentées)

3 stratégies acceptables :

**A. Benchmarks publics** :
- Recherche « ResNet-18 inference time CPU 224 » → article cité
- HuggingFace model card mentionne souvent les FLOPS / latence

**B. Mini-prototype 10 lignes** :
- Pour CLIP non implémenté : tu peux quand même charger le modèle et
  mesurer **juste la latence d'inférence** sur 1-5 images sans rien
  entraîner. 5 min de code.

**C. Extrapolation** :
- Si tu connais la latence sur GPU, divise par 5-10 pour estimer CPU
- Si tu connais le temps train sur 100 images, multiplie pour 1500

**Toujours citer** la source de l'estimation. *« Selon
[Sharma et al. 2022](url), ResNet-18 fait ~30 ms / image en CPU
PyTorch. »*

### Tableau type

| Critère | Option A (CNN) | Option B (Transfer) | Option C (CLIP) |
|---|---|---|---|
| **Status** | Mesuré | Estimé (source X) | Mesuré (mini-proto) |
| **Données train requises** | ~1500 | ~1500 | **0** |
| **Temps train CPU** | 8 min | ~4 min (estimé) | 0 |
| **Latence inférence (CPU)** | 12 ms | ~50 ms (estimé) | 150 ms |
| **Mémoire modèle** | 5 Mo | ~50 Mo | 600 Mo |
| **Accuracy attendue** | 80 % (mesuré) | 92 % (est., benchmark X) | 50 % (mesuré mini-proto) |

## Exemple minimal — verdict type structuré

```markdown
**Recommandation** : Transfer learning ResNet-18.

**Raison principale** : meilleur compromis précision/coût (92 % accuracy
estimée, 50 Mo mémoire, ~4 min train CPU). Vs CLIP zero-shot (50 % seulement
sur PCB — domaine trop spécifique pour les prompts génériques).

**Condition de changement d'avis** : si TechniMatic veut **un MVP sans
données labellisées** → CLIP zero-shot accepté malgré la précision moindre.
```

## Exercice guidé

Construis le **tableau économique comparatif des 3 approches** (même si tu n'en
implémentes qu'une) :

1. Une ligne par approche (CNN from scratch / Transfer / CLIP zero-shot).
2. Colonnes : **coût d'entraînement** (temps + données labellisées nécessaires),
   **coût d'inférence** (latence, mémoire), **précision estimée**, **maintenance**.
3. Les chiffres des 2 approches non implémentées peuvent venir des **ordres de
   grandeur** des mini-cours / de la littérature — **cite ta source**.
4. Rédige le verdict au format ci-dessus, avec une **condition de changement
   d'avis** explicite.

**Attendu** : un arbitrage **multi-critères** (pas juste « le plus précis ») qui
intègre le coût et le contexte client — exactement le geste C4 « choisir un
modèle adapté ».

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Estimations sans source | Inès te dira « tu me donnes des chiffres en l'air ? » — impardonnable |
| Comparer GPU benchmarks à CPU | Différence x5-x10 — toujours préciser le matos |
| Pas distinguer mesuré / estimé | Tu mens par omission — toujours indiquer le status |
| Oublier la mémoire / latence | Tableau unidimensionnel inutile |
| Ne pas mentionner les conditions de changement d'avis | Tu fais l'oracle, pas le consultant |

## Pour aller plus loin

- **MLPerf** (benchmarks de référence coût/perf) : <https://mlcommons.org/benchmarks/>
- **Green AI** (Schwartz et al., 2019) — le coût énergétique comme critère :
  <https://arxiv.org/abs/1907.10597>
- Doc **torch.cuda** / profilage : mesurer mémoire et temps d'inférence proprement.
- Lien éco-conception : un modèle plus léger (transfer < CNN scratch < gros
  modèle) = moins de calcul = moins d'empreinte. À mentionner dans le verdict.

## Vérification

- [ ] Tableau avec **6+ critères**
- [ ] Distinction claire **mesuré / estimé**
- [ ] **Sources citées** pour les estimations
- [ ] Verdict avec **3 sections** : recommandation + raison chiffrée + condition de changement
- [ ] Pas de comparaison apple-to-orange (CPU vs GPU)
