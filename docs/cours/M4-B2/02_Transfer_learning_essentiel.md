# Transfer learning — Mini-cours

> Brief associé : M4-B2 (option B — souvent le meilleur compromis)
> Durée : ~20 min
> Pré-requis : PyTorch installé, notion de CNN.

## Pourquoi cette techno ?

Un **modèle pré-entraîné** sur **ImageNet** (1.4 M images, 1000 classes)
a déjà appris à **détecter des features visuelles** (bords, textures,
motifs) — ces features sont **réutilisables** sur ton dataset PCB.

Tu **freeze** la majorité des couches (les features sont bonnes telles
quelles), et tu **fine-tunes** la dernière couche pour tes 7 classes PCB.

**Avantages** :
- Moins de données nécessaires (~100 par classe peut suffire)
- Entraînement **beaucoup plus rapide** (3-5 epochs)
- Précision **souvent supérieure** à CNN scratch sur datasets moyens

**C'est presque toujours le bon choix** pour la vision quand tu as
< 100 k images et que tu n'es pas dans un domaine ultra-spécifique.

## Concepts clés

### ResNet-18 — le défaut moderne

ResNet-18 (11.7 M paramètres) est le **starter pack** transfer
learning :
- Pré-entraîné sur ImageNet
- Petit, rapide à fine-tuner
- Disponible dans `torchvision.models`

Alternatives : ResNet-50 (plus précis, plus lent), ViT-Small (transformer,
plus moderne).

### Workflow type

```python
from torchvision import models, transforms
import torch.nn as nn

# 1. Charge ResNet-18 pré-entraîné
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

# 2. Freeze toutes les couches
for param in model.parameters():
    param.requires_grad = False

# 3. Remplace la dernière couche pour 7 classes PCB
model.fc = nn.Linear(model.fc.in_features, 7)
# Cette nouvelle couche est `requires_grad=True` par défaut

# 4. Adapter les inputs : PCB est 1×64×64 grayscale, ResNet attend 3×224×224 RGB
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),  # 1→3 canaux
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],   # ImageNet stats
                         std=[0.229, 0.224, 0.225]),
])

# 5. Entraîne (seule la nouvelle couche fc apprend)
import torch.optim as optim
optimizer = optim.Adam(model.fc.parameters(), lr=1e-3)
# (3-5 epochs suffisent)
```

### Variantes

- **Freeze partiel** : freeze tout sauf les **2 derniers blocs**. Plus de
  paramètres entraînables = plus de capacité d'adaptation, plus de risque
  d'overfit. À tester si freeze full sous-performant.
- **Pas de freeze** : tout fine-tuner. Très coûteux, justifié uniquement
  pour gros datasets.

## Exemple minimal qui tourne

On part d'un **ResNet18 pré-entraîné sur ImageNet**, on **gèle** le backbone et
on remplace juste la **tête** par une couche adaptée à nos 7 classes.

```python
# torch==2.5.0, torchvision==0.20.0
import torch
import torch.nn as nn
from torchvision import models

model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

for param in model.parameters():        # on gèle tout le backbone pré-entraîné
    param.requires_grad = False

model.fc = nn.Linear(model.fc.in_features, 7)   # nouvelle tête : 512 → 7 classes

trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
frozen = sum(p.numel() for p in model.parameters() if not p.requires_grad)
print(f"Entraînables : {trainable} | gelés : {frozen}")   # ~3 591 vs ~11 M

dummy = torch.randn(2, 3, 224, 224)     # ResNet attend 3 canaux, 224×224
print(model(dummy).shape)               # → torch.Size([2, 7])
```

Tu n'entraînes que ~3 600 poids (la tête) au lieu de 11 millions : c'est tout
l'intérêt du transfer learning sur un petit dataset.

## Exercice guidé

1. Nos images PCB sont en **niveaux de gris 64×64**, mais ResNet veut du **RGB
   224×224**. Quelle transformation `torchvision` appliquer ? (indice :
   `transforms.Grayscale(num_output_channels=3)` + `transforms.Resize(224)`).
2. Complète `build_resnet18_classifier` dans `src/option_b_transfer.py` et
   vérifie la sortie `(batch, 7)`.
3. **Dégèle les 2 derniers blocs** (`layer4` + `fc`) et compare : meilleure
   précision ? entraînement plus lent ? C'est l'arbitrage *feature extraction*
   vs *fine-tuning*.

**Attendu** : tu sais adapter une image à l'entrée d'un modèle pré-entraîné et
expliquer pourquoi geler le backbone suffit souvent sur peu de données.

## Performance : ça dépend du domaine (mesure, ne présuppose pas)

Le transfer learning **n'est pas une garantie de performance**. Il dépend
surtout de l'**alignement entre le domaine d'origine** (ImageNet = photos
naturelles RGB) **et ton domaine cible** :
- domaine **proche** d'ImageNet → le transfer domine souvent le CNN scratch ;
- domaine **éloigné** (images abstraites, synthétiques, très hors-distribution)
  → le backbone **gelé** peut au contraire **sous-performer** un simple CNN
  entraîné sur tes données. C'est le **negative transfer** : le pré-entraînement
  *dégrade* au lieu d'aider. Le **fine-tuning** (dé-gel) peut alors le rattraper,
  au prix du temps de calcul.

- **Temps train CPU** : ~3-5 min (5 epochs, gelé) — plus lourd que le CNN scratch
- **Mémoire** : ~45 Mo (ResNet-18)
- **Accuracy** : **à MESURER sur ton dataset** — ne la présuppose pas. Le
  résultat peut surprendre (c'est tout l'intérêt de la comparaison C4).

> 🔒 **Verrou** : ni « le transfer gagne toujours », ni « le transfer est nul »
> ne sont vrais. **Aucune approche n'est universellement meilleure** — le
> classement dépend du **contexte** (proximité de domaine, gel vs fine-tuning,
> volume de données, budget). Un mauvais score en transfer **gelé** signifie
> « inadapté **à ce domaine sans adaptation** », pas « transfer inutile ».

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Forgot `transforms.Grayscale(3)` sur images 1 canal | ResNet attend 3 canaux, crash |
| Forgot la normalisation ImageNet | Performance dégradée |
| Forgot de freeze | Tout fine-tuner = très lent + overfit |
| Forgot `model.fc = nn.Linear(...)` | Sortie 1000 classes au lieu de 7 |
| `lr` trop élevé sur fc (1e-1) | Divergence — reste à 1e-3 |
| Resize plus petit que 224 | Performances dégradées (ResNet entraîné sur 224) |

## Pour aller plus loin

- **PyTorch — Transfer learning tutorial** : <https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html>
- **torchvision.models** : <https://pytorch.org/vision/stable/models.html>

## Vérification

- [ ] ResNet-18 chargé avec weights pré-entraînés
- [ ] Backbone freezé (verify : `sum(p.requires_grad for p in model.parameters())` retourne seulement la dernière FC)
- [ ] Transforms : Grayscale(3) + Resize 224 + Normalize ImageNet
- [ ] Entraînement 3-5 epochs, accuracy > 85 % attendue
- [ ] Modèle persisté
