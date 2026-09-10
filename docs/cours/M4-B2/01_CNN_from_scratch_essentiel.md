# CNN from scratch — Mini-cours

> Brief associé : M4-B2 (option A)
> Durée : ~25 min
> Pré-requis : notion de réseau de neurones, PyTorch installé.

## Pourquoi cette techno ?

**Construire ton propre CNN** est l'approche **la plus didactique** pour
comprendre comment fonctionne un réseau de convolution. Tu vois chaque
couche, chaque paramètre. Tu maîtrises tout.

**Inconvénients** :
- Demande **beaucoup de données** pour bien généraliser (typiquement
  10 k+ images par classe)
- Sur PCB Defect (~300 par classe), **risque de sous-apprentissage**
- **Temps d'entraînement** plus long que transfer learning

**Quand préférer CNN scratch** :
- Domaine très spécifique sans backbone pré-entraîné pertinent
- Beaucoup de données disponibles
- Besoin de comprendre l'architecture pour expliquer

**Quand éviter** :
- Peu de données (< 1 k par classe) — préfère transfer learning
- Délai court — transfer learning ou zero-shot plus rapide
- Précision critique — boosting / transfer plus performants

**Sur PCB Defect 2 100 images** : CNN scratch est **viable** mais
probablement **dominé** par transfer learning en précision. Bonne
référence pédagogique néanmoins.

## Concepts clés

### Architecture suggérée pour PCB 64×64

```python
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self, n_classes=7):
        super().__init__()
        # Bloc 1 : 1×64×64 → 16×32×32
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.pool1 = nn.MaxPool2d(2, 2)
        # Bloc 2 : 16×32×32 → 32×16×16
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool2 = nn.MaxPool2d(2, 2)
        # Bloc 3 : 32×16×16 → 64×8×8
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool3 = nn.MaxPool2d(2, 2)
        # Dense head
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(64 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, n_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = self.pool1(self.relu(self.conv1(x)))
        x = self.pool2(self.relu(self.conv2(x)))
        x = self.pool3(self.relu(self.conv3(x)))
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x
```

### Boucle d'entraînement

```python
import torch
import torch.optim as optim
import torch.nn as nn

model = SimpleCNN(n_classes=7).to(DEVICE)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

EPOCHS = 5  # 5-10 suffit en M4-B2
for epoch in range(EPOCHS):
    train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, DEVICE)
    val_loss, val_acc = evaluate(model, val_loader, criterion, DEVICE)
    print(f"Epoch {epoch}: train_acc {train_acc:.3f}, val_acc {val_acc:.3f}")
```

### Hyperparamètres clés

- **Batch size** : 32 (CPU OK)
- **Learning rate** : 1e-3 (Adam standard)
- **Epochs** : 5-10 (au-delà = overfitting probable sur 2 k images)
- **Dropout** : 0.2-0.3 (régularisation)

## Exemple minimal qui tourne

Un petit CNN pour images **64×64 en niveaux de gris** (1 canal), 7 classes. Le
point délicat est l'arithmétique des dimensions jusqu'au `flatten`.

```python
# torch==2.5.0
import torch
import torch.nn as nn


class SimpleCNN(nn.Module):
    def __init__(self, n_classes: int = 7) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)   # 1 canal (N&B)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(32 * 16 * 16, 128)   # 64 →(pool) 32 →(pool) 16
        self.fc2 = nn.Linear(128, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(torch.relu(self.conv1(x)))   # 64 → 32
        x = self.pool(torch.relu(self.conv2(x)))   # 32 → 16
        x = x.flatten(1)
        x = torch.relu(self.fc1(x))
        return self.fc2(x)


model = SimpleCNN()
dummy = torch.randn(4, 1, 64, 64)        # batch de 4 images 64×64 N&B
print(model(dummy).shape)                # → torch.Size([4, 7])
```

Si ce `forward` tourne et sort `(batch, 7)`, ton architecture est cohérente —
tu peux brancher l'entraînement.

## Exercice guidé

1. Complète le `forward` de `src/option_a_cnn.py` (les couches sont en TODO).
2. Vérifie sur un batch factice que la sortie est bien `(batch, 7)`.
3. **Recalcule à la main** : si tu ajoutes un **3ᵉ bloc conv + pool**, quelle
   devient la taille d'entrée de `fc1` ? (indice : 16 → 8, donc `64 * 8 * 8`).
4. Ajoute un `nn.Dropout(0.25)` avant `fc2` — à quoi ça sert sur un petit dataset ?

**Attendu** : tu sais relier la taille des images, le nombre de pools et la
dimension du `flatten` — l'erreur n°1 des débutants en CNN.

## Performance attendue sur PCB

- **Accuracy** : ~70-85 % (selon réglage et stratification)
- **Temps train CPU** : ~5-15 min sur les 5-10 epochs
- **Mémoire** : ~5-10 Mo (modèle compact)

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Trop d'epochs (50+) | Overfit massif sur 2 k images |
| Pas de validation set | Tu ne sais pas si tu généralises |
| Batch size 256+ sur CPU | Très lent — reste à 32 |
| Forgot `model.eval()` à l'évaluation | Dropout actif = scores incohérents |
| Forgot `optimizer.zero_grad()` | Gradients accumulent — convergence chaotique |
| `lr` trop élevé (>1e-2) | Divergence — préfère 1e-3 ou 1e-4 |

## Pour aller plus loin

- **PyTorch — Quickstart** : <https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html>
- **CNN explained** : <https://cs231n.github.io/convolutional-networks/>
  (Stanford CS231n — référence)

## Vérification

- [ ] Architecture définie + forward fonctionnel
- [ ] Boucle train/val sur ≥ 3 epochs
- [ ] Accuracy mesurée sur train + val
- [ ] Modèle persisté (`torch.save`)
- [ ] Pas d'overfit catastrophique (val_acc ne s'effondre pas)
